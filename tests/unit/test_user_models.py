"""
Unit tests for User application models.
Tests User, UserAddress, UserWishlist models.
"""

import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestUser:
    """Tests for User model"""
    
    def test_user_creation(self, db):
        """Test creating a regular user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.check_password('testpass123') is True
        assert str(user) == 'Test User'
    
    def test_user_password(self, db):
        """Test user password is hashed"""
        user = User.objects.create_user(
            username='testpassuser',
            email='testpass@example.com',
            password='testpass123'
        )
        
        assert user.check_password('testpass123') is True
        assert user.password != 'testpass123'  # Should be hashed
    
    def test_staff_user_creation(self, db):
        """Test creating a staff user"""
        user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        assert user.is_staff is True
        assert user.is_superuser is False
    
    def test_admin_user_creation(self, db):
        """Test creating an admin user"""
        user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123'
        )
        
        assert user.is_staff is True
        assert user.is_superuser is True
    
    def test_user_str(self, db):
        """Test string representation of user"""
        user = User.objects.create_user(
            username='john',
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        assert str(user) == 'John Doe'
    
    def test_user_get_full_name(self, db):
        """Test user get_full_name method"""
        user = User.objects.create_user(
            username='johndoe',
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        assert user.get_full_name() == 'John Doe'
    
    def test_user_get_short_name(self, db):
        """Test user get_short_name method"""
        user = User.objects.create_user(
            username='john',
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        assert user.get_short_name() == 'John'
    
    def test_user_email_unique(self, db):
        """Test that user emails are unique"""
        User.objects.create_user(
            username='user1',
            email='unique@example.com',
            password='pass123'
        )
        
        with pytest.raises(Exception):
            User.objects.create_user(
                username='user2',
                email='unique@example.com',
                password='pass456'
            )
    
    def test_user_username_unique(self, db):
        """Test that user usernames are unique"""
        User.objects.create_user(
            username='uniqueuser',
            email='test1@example.com',
            password='pass123'
        )
        
        with pytest.raises(Exception):
            User.objects.create_user(
                username='uniqueuser',
                email='test2@example.com',
                password='pass456'
            )


class TestUserAddress:
    """Tests for UserAddress model"""
    
    def test_user_address_creation(self, db):
        """Test creating a user address"""
        from apps.accounts.models import UserAddress
        user = User.objects.create_user(
            username='addressuser',
            email='address@example.com',
            password='pass123'
        )
        address = UserAddress.objects.create(
            user=user,
            address_type='home',
            recipient_name='John Doe',
            phone_number='+123456789',
            address_line_1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            country='US'
        )
        
        assert address.user == user
        assert address.address_type == 'home'
        assert address.recipient_name == 'John Doe'
        assert address.city == 'New York'
        assert address.state == 'NY'
        assert address.postal_code == '10001'
        assert address.country == 'US'
        assert address.is_default is False
        assert str(address) == 'John Doe - New York'
    
    def test_user_address_str(self, db):
        """Test string representation of user address"""
        from apps.accounts.models import UserAddress
        user = User.objects.create_user(
            username='jane',
            email='jane@example.com',
            password='pass123'
        )
        address = UserAddress.objects.create(
            user=user,
            address_type='work',
            recipient_name='Jane Smith',
            phone_number='+987654321',
            address_line_1='456 Oak Ave',
            city='Los Angeles',
            state='CA',
            postal_code='90001'
        )
        assert str(address) == 'Jane Smith - Los Angeles'
    
    def test_user_address_types(self, db):
        """Test different address types"""
        from apps.accounts.models import UserAddress
        user = User.objects.create_user(
            username='addresstypeuser',
            email='type@example.com',
            password='pass123'
        )
        
        home = UserAddress.objects.create(
            user=user, 
            address_type='home',
            recipient_name='Test',
            phone_number='+111',
            address_line_1='123 St',
            city='City',
            state='ST',
            postal_code='12345'
        )
        work = UserAddress.objects.create(
            user=user,
            address_type='work',
            recipient_name='Test',
            phone_number='+222',
            address_line_1='456 St',
            city='City',
            state='ST',
            postal_code='12345'
        )
        other = UserAddress.objects.create(
            user=user,
            address_type='other',
            recipient_name='Test',
            phone_number='+333',
            address_line_1='789 St',
            city='City',
            state='ST',
            postal_code='12345'
        )
        
        assert home.address_type == 'home'
        assert work.address_type == 'work'
        assert other.address_type == 'other'
    
    def test_user_address_default(self, db):
        """Test default address"""
        from apps.accounts.models import UserAddress
        user = User.objects.create_user(
            username='defaultuser',
            email='default@example.com',
            password='pass123'
        )
        address = UserAddress.objects.create(
            user=user,
            address_type='home',
            recipient_name='John Doe',
            phone_number='+123456789',
            address_line_1='123 Main St',
            city='New York',
            state='NY',
            postal_code='10001',
            is_default=True
        )
        
        assert address.is_default is True
        assert str(address) == 'John Doe - New York'
    
    def test_user_address_unique_default(self, db):
        """Test only one default address per user"""
        from apps.accounts.models import UserAddress
        user = User.objects.create_user(
            username='uniquedefault',
            email='unique@example.com',
            password='pass123'
        )
        
        address1 = UserAddress.objects.create(
            user=user,
            address_type='home',
            recipient_name='John Doe',
            phone_number='+111',
            address_line_1='123 St',
            city='City1',
            state='ST',
            postal_code='12345',
            is_default=True
        )
        
        address2 = UserAddress.objects.create(
            user=user,
            address_type='work',
            recipient_name='John Doe',
            phone_number='+222',
            address_line_1='456 St',
            city='City2',
            state='ST',
            postal_code='12345',
            is_default=True
        )
        
        # Refresh first address from database
        address1.refresh_from_db()
        assert address1.is_default is False
        assert address2.is_default is True


class TestUserWishlist:
    """Tests for UserWishlist model"""
    
    def test_wishlist_creation(self, db):
        """Test creating a wishlist"""
        from apps.accounts.models import UserWishlist
        from apps.products.models import Product
        
        user = User.objects.create_user(
            username='wishlistuser',
            email='wishlist@example.com',
            password='pass123'
        )
        product = Product.objects.create(
            sku='PROD001',
            name='Test Product',
            slug='test-product',
            regular_price=100.00
        )
        
        wishlist = UserWishlist.objects.create(
            user=user,
            product=product
        )
        
        assert wishlist.user == user
        assert wishlist.product == product
        assert str(wishlist) == f"{user} - {product}"
    
    def test_wishlist_unique_per_user_product(self, db):
        """Test wishlist unique constraint per user and product"""
        from apps.accounts.models import UserWishlist
        from apps.products.models import Product
        
        user = User.objects.create_user(
            username='uniquewishlist',
            email='uniquew@example.com',
            password='pass123'
        )
        product = Product.objects.create(
            sku='PROD002',
            name='Unique Product',
            slug='unique-product',
            regular_price=100.00
        )
        
        UserWishlist.objects.create(user=user, product=product)
        
        with pytest.raises(Exception):
            UserWishlist.objects.create(user=user, product=product)
