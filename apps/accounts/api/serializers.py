"""
Serializers for Accounts API.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import UserProfile, UserAddress, Wishlist

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'avatar', 'gender',
            'birth_date', 'newsletter_subscribed'
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True},
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'password', 'password_confirm', 'avatar',
            'gender', 'birth_date', 'newsletter_subscribed'
        ]
    
    def validate(self, data):
        """Validate password match."""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            **{k: v for k, v in validated_data.items() if k not in ['password', 'username', 'email']}
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'avatar',
            'gender', 'birth_date', 'newsletter_subscribed'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'bio', 'website', 'social_facebook',
            'social_twitter', 'social_instagram', 'social_linkedin',
            'preferred_language', 'preferred_currency',
            'notification_preferences', 'privacy_settings',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class UserAddressSerializer(serializers.ModelSerializer):
    """Serializer for UserAddress model."""
    
    class Meta:
        model = UserAddress
        fields = [
            'id', 'user', 'address_type', 'first_name', 'last_name',
            'company', 'address_line_1', 'address_line_2', 'city',
            'state', 'postal_code', 'country', 'phone',
            'is_default', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model."""
    
    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'name', 'is_public', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist items (from products)."""
    
    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'name', 'is_public', 'is_default',
            'created_at', 'updated_at', 'items_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'items_count']


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    remember_me = serializers.BooleanField(default=False)
    
    class Meta:
        fields = ['username', 'password', 'remember_me']


class UserLoginResponseSerializer(serializers.Serializer):
    """Serializer for login response."""
    
    user = UserSerializer()
    token = serializers.CharField()
    expires_at = serializers.DateTimeField()
    
    class Meta:
        fields = ['user', 'token', 'expires_at']


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change."""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        fields = ['old_password', 'new_password', 'new_password_confirm']
    
    def validate(self, data):
        """Validate password match."""
        if data.get('new_password') != data.get('new_password_confirm'):
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match'})
        return data


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField(required=True)
    
    class Meta:
        fields = ['email']


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        fields = ['token', 'new_password', 'new_password_confirm']
    
    def validate(self, data):
        """Validate password match."""
        if data.get('new_password') != data.get('new_password_confirm'):
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match'})
        return data


class OTPLoginSerializer(serializers.Serializer):
    """Serializer for OTP login."""
    
    phone = serializers.CharField(required=True)
    
    class Meta:
        fields = ['phone']


class OTPVerifySerializer(serializers.Serializer):
    """Serializer for OTP verification."""
    
    phone = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)
    
    class Meta:
        fields = ['phone', 'otp']


class UserDashboardSerializer(serializers.Serializer):
    """Serializer for user dashboard data."""
    
    user = UserSerializer()
    profile = UserProfileSerializer(required=False, allow_null=True)
    addresses_count = serializers.IntegerField()
    wishlists_count = serializers.IntegerField()
    orders_count = serializers.IntegerField()
    recent_orders = serializers.ListField(child=serializers.DictField())
    wishlist_items_count = serializers.IntegerField()
    
    class Meta:
        fields = [
            'user', 'profile', 'addresses_count', 'wishlists_count',
            'orders_count', 'recent_orders', 'wishlist_items_count'
        ]
