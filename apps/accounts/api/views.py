"""
API views for Accounts app.
"""
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models import UserProfile, UserAddress, Wishlist
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserProfileSerializer, UserAddressSerializer, WishlistSerializer,
    UserLoginSerializer, UserLoginResponseSerializer,
    PasswordChangeSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, OTPLoginSerializer,
    OTPVerifySerializer, UserDashboardSerializer
)

User = get_user_model()


# User Views
class UserListAPIView(generics.ListAPIView):
    """List all users (admin only)."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Filter users."""
        queryset = User.objects.all().order_by('-date_joined')
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        
        # Filter by staff status
        is_staff = self.request.query_params.get('is_staff')
        if is_staff:
            queryset = queryset.filter(is_staff=(is_staff.lower() == 'true'))
        
        # Search
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(username__icontains=query) | 
                models.Q(email__icontains=query) | 
                models.Q(first_name__icontains=query) | 
                models.Q(last_name__icontains=query)
            )
        
        return queryset


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve user details."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get current user or specified user."""
        if self.request.user.is_superuser:
            pk = self.kwargs.get('pk')
            if pk:
                return get_object_or_404(User, pk=pk)
        return self.request.user


class UserCreateAPIView(generics.CreateAPIView):
    """Create a new user."""
    
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserUpdateAPIView(generics.UpdateAPIView):
    """Update user profile."""
    
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get current user."""
        return self.request.user


class UserDeleteAPIView(generics.DestroyAPIView):
    """Delete user account."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get current user."""
        return self.request.user


# Authentication Views
class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain pair view with user data."""
    
    serializer_class = UserLoginSerializer
    
    def validate(self, attrs):
        """Validate credentials and return token with user data."""
        data = super().validate(attrs)
        
        # Add user data to response
        user = self.user
        refresh = self.get_tokens_for_user(user)
        
        data.update({
            'user': UserSerializer(user).data,
            'expires_at': timezone.now() + timezone.timedelta(days=1)
        })
        
        return data


class UserLoginAPIView(views.APIView):
    """User login with username/email and password."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Authenticate user and return token."""
        serializer = UserLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        remember_me = serializer.validated_data.get('remember_me', False)
        
        # Find user by username or email
        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                pass
        
        if not user or not check_password(password, user.password):
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'detail': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate token
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'expires_at': timezone.now() + timezone.timedelta(
                days=30 if remember_me else 1
            )
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        
        # Set cookies if remember_me
        if remember_me:
            response.set_cookie(
                'refresh_token',
                str(refresh),
                max_age=30 * 24 * 60 * 60,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        return response


class UserLogoutAPIView(views.APIView):
    """User logout."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user by invalidating token."""
        # In JWT, logout is handled client-side by removing the token
        # We can optionally blacklist the token
        
        response = Response(
            {'detail': 'Successfully logged out'},
            status=status.HTTP_200_OK
        )
        
        # Clear refresh token cookie
        response.delete_cookie('refresh_token')
        
        return response


class PasswordChangeAPIView(views.APIView):
    """Change user password."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Change password."""
        serializer = PasswordChangeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not check_password(old_password, user.password):
            return Response(
                {'old_password': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'detail': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )


# OTP Views
class OTPLoginAPIView(views.APIView):
    """Request OTP for login."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Send OTP to phone number."""
        serializer = OTPLoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        
        # Find or create user with this phone
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={
                'username': phone,
                'email': f'{phone}@otp.login'
            }
        )
        
        # Generate OTP (in production, use a proper OTP service)
        import random
        otp = str(random.randint(100000, 999999))
        
        # Store OTP in session or cache
        from django.core.cache import cache
        cache.set(f'otp_{phone}', otp, timeout=300)  # 5 minutes
        
        # In production, send OTP via SMS
        # For now, return OTP in response (for testing only)
        if settings.DEBUG:
            return Response(
                {'detail': 'OTP sent successfully', 'otp': otp},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'detail': 'OTP sent successfully'},
            status=status.HTTP_200_OK
        )


class OTPVerifyAPIView(views.APIView):
    """Verify OTP and login."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Verify OTP and return token."""
        serializer = OTPVerifySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        otp = serializer.validated_data['otp']
        
        # Get stored OTP
        from django.core.cache import cache
        stored_otp = cache.get(f'otp_{phone}')
        
        if not stored_otp or stored_otp != otp:
            return Response(
                {'detail': 'Invalid OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clear OTP
        cache.delete(f'otp_{phone}')
        
        # Find user
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'expires_at': timezone.now() + timezone.timedelta(days=30)
        }, status=status.HTTP_200_OK)


# Profile Views
class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """Retrieve and update user profile."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create user profile."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


# Address Views
class UserAddressListCreateAPIView(generics.ListCreateAPIView):
    """List and create user addresses."""
    
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's addresses."""
        return UserAddress.objects.filter(user=self.request.user).order_by('-is_default', '-created_at')
    
    def perform_create(self, serializer):
        """Create address for current user."""
        serializer.save(user=self.request.user)


class UserAddressRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete user address."""
    
    serializer_class = UserAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's addresses."""
        return UserAddress.objects.filter(user=self.request.user)


class UserAddressSetDefaultAPIView(views.APIView):
    """Set an address as default."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Set address as default."""
        address = get_object_or_404(UserAddress, pk=pk, user=request.user)
        
        # Reset all default addresses
        UserAddress.objects.filter(user=request.user).update(is_default=False)
        
        # Set this as default
        address.is_default = True
        address.save()
        
        serializer = UserAddressSerializer(address)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Wishlist Views
class WishlistListCreateAPIView(generics.ListCreateAPIView):
    """List and create wishlists."""
    
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's wishlists."""
        return Wishlist.objects.filter(user=self.request.user).order_by('-is_default', '-created_at')
    
    def perform_create(self, serializer):
        """Create wishlist for current user."""
        serializer.save(user=self.request.user)


class WishlistRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete wishlist."""
    
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's wishlists."""
        return Wishlist.objects.filter(user=self.request.user)


class WishlistSetDefaultAPIView(views.APIView):
    """Set a wishlist as default."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        """Set wishlist as default."""
        wishlist = get_object_or_404(Wishlist, pk=pk, user=request.user)
        
        # Reset all default wishlists
        Wishlist.objects.filter(user=request.user).update(is_default=False)
        
        # Set this as default
        wishlist.is_default = True
        wishlist.save()
        
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Dashboard View
class UserDashboardAPIView(views.APIView):
    """Get user dashboard data."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Return dashboard data."""
        user = request.user
        
        # Get profile
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = None
        
        # Count addresses
        addresses_count = UserAddress.objects.filter(user=user).count()
        
        # Count wishlists
        wishlists_count = Wishlist.objects.filter(user=user).count()
        
        # Count orders
        from apps.orders.models import Order
        orders_count = Order.objects.filter(user=user).count()
        
        # Get recent orders
        recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
        recent_orders_data = [
            {
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'total': order.total_amount,
                'created_at': order.created_at
            }
            for order in recent_orders
        ]
        
        # Count wishlist items
        from apps.products.models import Product
        wishlist_items_count = 0
        
        # Get user's default wishlist
        default_wishlist = Wishlist.objects.filter(user=user, is_default=True).first()
        if default_wishlist:
            wishlist_items_count = default_wishlist.products.count()
        
        data = {
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(profile).data if profile else None,
            'addresses_count': addresses_count,
            'wishlists_count': wishlists_count,
            'orders_count': orders_count,
            'recent_orders': recent_orders_data,
            'wishlist_items_count': wishlist_items_count
        }
        
        serializer = UserDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# User Search
class UserSearchAPIView(generics.ListAPIView):
    """Search users (admin only)."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Search users."""
        queryset = User.objects.all().order_by('-date_joined')
        
        query = self.request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                models.Q(username__icontains=query) | 
                models.Q(email__icontains=query) | 
                models.Q(first_name__icontains=query) | 
                models.Q(last_name__icontains=query) | 
                models.Q(phone__icontains=query)
            )
        
        return queryset[:20]  # Limit to 20 results
