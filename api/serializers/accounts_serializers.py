"""
Accounts Serializers
Serializers for accounts models: User, UserProfile, UserAddress, Wishlist
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.accounts.models import UserProfile, UserAddress, Wishlist
from apps.products.models import Product
from .products_serializers import ProductListSerializer


User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """Lightweight serializer for public user information"""
    
    full_name = serializers.SerializerMethodField(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'avatar_url', 'is_active']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')


class UserAddressSerializer(serializers.ModelSerializer):
    """Serializer for UserAddress model"""
    
    user = UserPublicSerializer(read_only=True)
    is_default = serializers.BooleanField(required=False, default=False)
    full_address = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = UserAddress
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'full_address')
    
    def get_full_address(self, obj):
        return obj.get_full_address()


class UserAddressListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for user address lists"""
    
    full_address = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = UserAddress
        fields = ['id', 'address_type', 'full_name', 'phone', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'is_default', 'full_address']
        read_only_fields = fields
    
    def get_full_address(self, obj):
        return obj.get_full_address()


class UserSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for User model"""
    
    profile = UserProfileSerializer(read_only=True)
    addresses = UserAddressSerializer(many=True, read_only=True)
    wishlist_count = serializers.SerializerMethodField(read_only=True)
    order_count = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)
    avatar_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'avatar_url', 'phone', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login', 'profile', 'addresses', 'wishlist_count', 'order_count']
        read_only_fields = ['id', 'date_joined', 'last_login', 'profile', 'addresses', 'wishlist_count', 'order_count', 'is_staff', 'is_superuser']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            return self.context['request'].build_absolute_uri(obj.avatar.url)
        return None
    
    def get_wishlist_count(self, obj):
        return Wishlist.objects.filter(user=obj).count()
    
    def get_order_count(self, obj):
        from apps.orders.models import Order
        return Order.objects.filter(user=obj).count()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Passwords must match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    avatar = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'avatar']


class UserPasswordUpdateSerializer(serializers.Serializer):
    """Serializer for updating user password"""
    
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password2": "New passwords must match."})
        return attrs


class UserPasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset requests"""
    
    email = serializers.EmailField(required=True)


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password2": "Passwords must match."})
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token obtain pair serializer with user data"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        return token


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    remember_me = serializers.BooleanField(required=False, default=False)


class SocialLoginSerializer(serializers.Serializer):
    """Serializer for social login"""
    
    provider = serializers.CharField(required=True)
    access_token = serializers.CharField(required=True)


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model"""
    
    user = UserPublicSerializer(read_only=True)
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=True)
    added_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user', 'product', 'added_at')


class WishlistListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for wishlist lists"""
    
    product = ProductListSerializer(read_only=True)
    product_image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_image', 'added_at']
        read_only_fields = fields
    
    def get_product_image(self, obj):
        if obj.product and obj.product.primary_image:
            return self.context['request'].build_absolute_uri(obj.product.primary_image.image.url)
        return None


class WishlistCreateSerializer(serializers.Serializer):
    """Serializer for adding to wishlist"""
    
    product_id = serializers.IntegerField(required=True)


class WishlistRemoveSerializer(serializers.Serializer):
    """Serializer for removing from wishlist"""
    
    product_id = serializers.IntegerField(required=True)


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    staff_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    new_users_this_week = serializers.IntegerField()
    user_growth = serializers.FloatField()
