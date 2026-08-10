"""
Accounts API Views
ViewSets and APIViews for accounts models
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile, UserAddress, Wishlist
from api.serializers.accounts_serializers import (
    UserSerializer,
    UserPublicSerializer,
    UserProfileSerializer,
    UserAddressSerializer,
    UserAddressListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserPasswordUpdateSerializer,
    UserPasswordResetSerializer,
    UserPasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    WishlistSerializer,
    WishlistListSerializer,
    WishlistCreateSerializer,
    WishlistRemoveSerializer,
    UserStatsSerializer,
)
from api.pagination import CustomPageNumberPagination


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True).order_by('-date_joined')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser', 'email']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['date_joined', 'last_login', 'email']
    pagination_class = CustomPageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserPublicSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'login', 'register']:
            return [AllowAny()]
        elif self.action in ['me', 'update', 'partial_update', 'password_change']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'activated', 'id': user.id})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'deactivated', 'id': user.id})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        from apps.orders.models import Order
        from apps.reviews.models import Review
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
            'new_users_today': User.objects.filter(date_joined__date=self.request.date_today).count(),
            'new_users_this_week': User.objects.filter(date_joined__week=self.request.date_today.isocalendar()[1]).count(),
            'user_growth': 0
        }
        
        # Calculate growth
        yesterday_count = User.objects.filter(date_joined__date=self.request.date_today - timedelta(days=1)).count()
        if yesterday_count > 0:
            stats['user_growth'] = ((stats['new_users_today'] - yesterday_count) / yesterday_count) * 100
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class UserRegistrationAPIView(APIView):
    """APIView for user registration"""
    
    permission_classes = [AllowAny]
    serializer_class = UserCreateSerializer
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': 'success',
                'user': UserSerializer(user, context={'request': request}).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(TokenObtainPairView):
    """APIView for user login"""
    
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class UserLogoutAPIView(APIView):
    """APIView for user logout"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'status': 'success', 'message': 'Successfully logged out'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetAPIView(APIView):
    """APIView for password reset request"""
    
    permission_classes = [AllowAny]
    serializer_class = UserPasswordResetSerializer
    
    def post(self, request):
        serializer = UserPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                # In production, send email with reset link
                # For now, just return success
                return Response({'status': 'success', 'message': 'Password reset email sent'})
            except User.DoesNotExist:
                return Response({'status': 'success', 'message': 'Password reset email sent'})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    """APIView for password reset confirmation"""
    
    permission_classes = [AllowAny]
    serializer_class = UserPasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = UserPasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # In production, verify token and update password
            # For now, just return success
            return Response({'status': 'success', 'message': 'Password has been reset'})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(APIView):
    """APIView for password change"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserPasswordUpdateSerializer
    
    def post(self, request):
        serializer = UserPasswordUpdateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            current_password = serializer.validated_data['current_password']
            new_password = serializer.validated_data['new_password']
            
            if not user.check_password(current_password):
                return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            # Invalidate all existing tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            for token in RefreshToken.objects.filter(user=user):
                token.blacklist()
            
            return Response({'status': 'success', 'message': 'Password changed successfully'})
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for UserProfile model"""
    
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    def get_object(self):
        if self.request.user.is_staff:
            return super().get_object()
        return UserProfile.objects.get(user=self.request.user)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]


class UserAddressViewSet(viewsets.ModelViewSet):
    """ViewSet for UserAddress model"""
    
    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['address_type', 'is_default', 'country']
    search_fields = ['full_name', 'phone', 'address_line_1', 'city', 'state', 'postal_code']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserAddressListSerializer
        return UserAddressSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        address = self.get_object()
        # Clear all default addresses for this user
        UserAddress.objects.filter(user=address.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save()
        return Response({'status': 'success', 'id': address.id})


class WishlistViewSet(viewsets.ModelViewSet):
    """ViewSet for Wishlist model"""
    
    serializer_class = WishlistSerializer
    queryset = Wishlist.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['product']
    search_fields = ['product__name', 'product__slug']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WishlistListSerializer
        elif self.action == 'create':
            return WishlistCreateSerializer
        elif self.action == 'destroy':
            return WishlistRemoveSerializer
        return WishlistSerializer
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        user = self.request.user
        
        # Check if already in wishlist
        if Wishlist.objects.filter(user=user, product=product).exists():
            return Response({'error': 'Product already in wishlist'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(user=user)
    
    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        product_ids = request.data.get('product_ids', [])
        user = request.user
        
        for product_id in product_ids:
            try:
                product = Product.objects.get(id=product_id)
                if not Wishlist.objects.filter(user=user, product=product).exists():
                    Wishlist.objects.create(user=user, product=product)
            except Product.DoesNotExist:
                pass
        
        return Response({'status': 'success'})
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        user = request.user
        Wishlist.objects.filter(user=user).delete()
        return Response({'status': 'success'})


class UserStatsAPIView(APIView):
    """APIView for user statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from apps.orders.models import Order
        from apps.reviews.models import Review
        from apps.cart.models import Cart
        
        user = request.user
        
        stats = {
            'wishlist_count': Wishlist.objects.filter(user=user).count(),
            'order_count': Order.objects.filter(user=user).count(),
            'review_count': Review.objects.filter(user=user).count(),
            'total_spent': sum(float(order.total) for order in Order.objects.filter(user=user, status='delivered')),
            'cart_item_count': Cart.objects.filter(user=user).count()
        }
        
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class UserMeAPIView(APIView):
    """APIView for current user details"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
