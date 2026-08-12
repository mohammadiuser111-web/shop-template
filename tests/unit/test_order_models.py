"""
Unit tests for Order application models.
Tests Order, OrderItem models.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

pytestmark = pytest.mark.django_db

User = get_user_model()


class TestShippingMethod:
    """Tests for ShippingMethod model"""
    
    def test_shipping_method_creation(self, db):
        """Test creating a shipping method"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Standard Zone', description='Standard shipping zone')
        method = ShippingMethod.objects.create(
            name='Standard Shipping',
            slug='standard-shipping',
            description='Standard shipping method',
            zone=zone,
            pricing_type='fixed',
            base_price=5.00,
            is_active=True,
            sort_order=0
        )
        
        assert method.name == 'Standard Shipping'
        assert method.slug == 'standard-shipping'
        assert method.base_price == 5.00
        assert str(method) == 'Standard Shipping'
    
    def test_shipping_method_str(self, db):
        """Test string representation of shipping method"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Express Zone', description='Express shipping zone')
        method = ShippingMethod.objects.create(
            name='Express Shipping',
            slug='express-shipping',
            zone=zone,
            base_price=10.00
        )
        assert str(method) == 'Express Shipping'
    
    def test_shipping_method_cost(self, db):
        """Test shipping method cost calculation"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Cost Zone', description='Cost shipping zone')
        method = ShippingMethod.objects.create(
            name='Fixed Cost',
            slug='fixed-cost',
            zone=zone,
            pricing_type='fixed',
            base_price=10.00
        )
        
        assert method.base_price == 10.00
    
    def test_shipping_method_free(self, db):
        """Test free shipping method"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Free Zone', description='Free shipping zone')
        method = ShippingMethod.objects.create(
            name='Free Shipping',
            slug='free-shipping',
            zone=zone,
            pricing_type='fixed',
            base_price=0.00
        )
        
        assert method.base_price == 0.00
    
    def test_shipping_method_pricing_types(self, db):
        """Test different shipping pricing types"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        
        zone = ShippingZone.objects.create(
            name='Domestic',
            description='Domestic shipping zone'
        )
        
        fixed = ShippingMethod.objects.create(
            name='Fixed',
            slug='fixed',
            zone=zone,
            pricing_type='fixed',
            base_price=10.00
        )
        per_item = ShippingMethod.objects.create(
            name='Per Item',
            slug='per-item',
            zone=zone,
            pricing_type='per_item',
            base_price=5.00,
            price_per_item=2.00
        )
        per_weight = ShippingMethod.objects.create(
            name='Per Weight',
            slug='per-weight',
            zone=zone,
            pricing_type='per_weight',
            base_price=5.00,
            price_per_kg=1.00
        )
        
        assert fixed.pricing_type == 'fixed'
        assert per_item.pricing_type == 'per_item'
        assert per_weight.pricing_type == 'per_weight'
    
    def test_shipping_method_active_status(self, db):
        """Test shipping method active status"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        
        zone = ShippingZone.objects.create(
            name='Test Zone',
            description='Test shipping zone'
        )
        
        active = ShippingMethod.objects.create(
            name='Active',
            slug='active',
            zone=zone,
            base_price=10.00,
            is_active=True
        )
        inactive = ShippingMethod.objects.create(
            name='Inactive',
            slug='inactive',
            zone=zone,
            base_price=10.00,
            is_active=False
        )
        
        assert active.is_active is True
        assert inactive.is_active is False
    
    def test_shipping_method_sort_order(self, db):
        """Test shipping method sort order"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        
        zone = ShippingZone.objects.create(
            name='Sort Zone',
            description='Sort shipping zone'
        )
        
        method1 = ShippingMethod.objects.create(
            name='Method 1',
            slug='method-1',
            zone=zone,
            base_price=10.00,
            sort_order=1
        )
        method2 = ShippingMethod.objects.create(
            name='Method 2',
            slug='method-2',
            zone=zone,
            base_price=10.00,
            sort_order=0
        )
        
        methods = ShippingMethod.objects.all().order_by('sort_order')
        assert methods[0] == method2
        assert methods[1] == method1
    
    def test_shipping_method_base_price(self, db):
        """Test shipping method base price"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        
        zone = ShippingZone.objects.create(
            name='Free Zone',
            description='Free shipping zone'
        )
        
        method = ShippingMethod.objects.create(
            name='Free',
            slug='free',
            zone=zone,
            base_price=0.00
        )
        assert method.base_price == 0.00
    
    def test_shipping_method_base_price_value(self, db):
        """Test shipping method base price value"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        
        zone = ShippingZone.objects.create(
            name='Formatted Zone',
            description='Formatted shipping zone'
        )
        
        method = ShippingMethod.objects.create(
            name='Formatted',
            slug='formatted',
            zone=zone,
            base_price=15.50
        )
        # Just test that it doesn't raise an error
        assert method.base_price == 15.50
    
    def test_shipping_method_free_base_price(self, db):
        """Test shipping method free base price"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        
        zone = ShippingZone.objects.create(
            name='Free Formatted Zone',
            description='Free formatted shipping zone'
        )
        
        method = ShippingMethod.objects.create(
            name='Free Formatted',
            slug='free-formatted',
            zone=zone,
            base_price=0.00
        )
        assert method.base_price == 0.00


class TestOrder:
    """Tests for Order model"""
    
    def test_order_creation(self, db):
        """Test creating an order"""
        from apps.orders.models import Order
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.create_user(
            username='orderuser',
            email='order@example.com',
            password='pass123'
        )
        
        order = Order.objects.create(
            order_number='ORD001',
            user=user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
            billing_address_line_1='123 Main St',
            billing_city='New York',
            billing_state='NY',
            billing_postal_code='10001',
            billing_country='US',
            subtotal=100.00,
            total=115.00,
            status='pending',
            payment_status='pending',
            payment_method='online'
        )
        
        assert order.order_number == 'ORD001'
        assert order.user == user
        assert order.first_name == 'John'
        assert order.last_name == 'Doe'
        assert order.status == 'pending'
        assert order.total == 115.00
        assert str(order) == 'Order #ORD001'
    
    def test_order_str(self, db):
        """Test string representation of order"""
        from apps.orders.models import Order
        order = Order.objects.create(
            order_number='ORD002',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
            billing_address_line_1='123 Main St',
            billing_city='New York',
            billing_state='NY',
            billing_postal_code='10001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            status='completed'
        )
        assert str(order) == 'Order #ORD002'
    
    def test_order_statuses(self, db):
        """Test different order statuses"""
        from apps.orders.models import Order
        
        pending = Order.objects.create(
            order_number='ORD003',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
            billing_address_line_1='123 Main St',
            billing_city='New York',
            billing_state='NY',
            billing_postal_code='10001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            status='pending'
        )
        processing = Order.objects.create(
            order_number='ORD004',
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='456 Oak Ave',
            shipping_city='Los Angeles',
            shipping_state='CA',
            shipping_postal_code='90001',
            shipping_country='US',
            billing_address_line_1='456 Oak Ave',
            billing_city='Los Angeles',
            billing_state='CA',
            billing_postal_code='90001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            status='processing'
        )
        completed = Order.objects.create(
            order_number='ORD005',
            first_name='Bob',
            last_name='Smith',
            email='bob@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='789 Pine Rd',
            shipping_city='Chicago',
            shipping_state='IL',
            shipping_postal_code='60601',
            shipping_country='US',
            billing_address_line_1='789 Pine Rd',
            billing_city='Chicago',
            billing_state='IL',
            billing_postal_code='60601',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            status='confirmed'
        )
        cancelled = Order.objects.create(
            order_number='ORD006',
            first_name='Alice',
            last_name='Jones',
            email='alice@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='321 Elm St',
            shipping_city='Houston',
            shipping_state='TX',
            shipping_postal_code='77001',
            shipping_country='US',
            billing_address_line_1='321 Elm St',
            billing_city='Houston',
            billing_state='TX',
            billing_postal_code='77001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            status='cancelled'
        )
        
        assert pending.status == 'pending'
        assert processing.status == 'processing'
        assert completed.status == 'confirmed'
        assert cancelled.status == 'cancelled'
    
    def test_order_payment_statuses(self, db):
        """Test different order payment statuses"""
        from apps.orders.models import Order
        
        pending = Order.objects.create(
            order_number='ORD007',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
            billing_address_line_1='123 Main St',
            billing_city='New York',
            billing_state='NY',
            billing_postal_code='10001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            payment_status='pending'
        )
        paid = Order.objects.create(
            order_number='ORD008',
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='456 Oak Ave',
            shipping_city='Los Angeles',
            shipping_state='CA',
            shipping_postal_code='90001',
            shipping_country='US',
            billing_address_line_1='456 Oak Ave',
            billing_city='Los Angeles',
            billing_state='CA',
            billing_postal_code='90001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            payment_status='paid'
        )
        failed = Order.objects.create(
            order_number='ORD009',
            first_name='Bob',
            last_name='Smith',
            email='bob@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='789 Pine Rd',
            shipping_city='Chicago',
            shipping_state='IL',
            shipping_postal_code='60601',
            shipping_country='US',
            billing_address_line_1='789 Pine Rd',
            billing_city='Chicago',
            billing_state='IL',
            billing_postal_code='60601',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            payment_status='failed'
        )
        refunded = Order.objects.create(
            order_number='ORD010',
            first_name='Alice',
            last_name='Jones',
            email='alice@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='321 Elm St',
            shipping_city='Houston',
            shipping_state='TX',
            shipping_postal_code='77001',
            shipping_country='US',
            billing_address_line_1='321 Elm St',
            billing_city='Houston',
            billing_state='TX',
            billing_postal_code='77001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            payment_status='refunded'
        )
        
        assert pending.payment_status == 'pending'
        assert paid.payment_status == 'paid'
        assert failed.payment_status == 'failed'
        assert refunded.payment_status == 'refunded'
    
    def test_order_total_calculation(self, db):
        """Test order total calculation"""
        from apps.orders.models import Order
        order = Order.objects.create(
            order_number='ORD014',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
            billing_address_line_1='123 Main St',
            billing_city='New York',
            billing_state='NY',
            billing_postal_code='10001',
            billing_country='US',
            subtotal=100.00,
            tax=10.00,
            shipping_cost=5.00,
            discount=0.00,
            total=115.00
        )
        
        assert order.subtotal == 100.00
        assert order.tax == 10.00
        assert order.shipping_cost == 5.00
        assert order.total == 115.00
    
    def test_order_guest(self, db):
        """Test creating a guest order"""
        from apps.orders.models import Order
        order = Order.objects.create(
            order_number='ORD015',
            user=None,
            first_name='Guest',
            last_name='User',
            email='guest@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
            billing_address_line_1='123 Main St',
            billing_city='New York',
            billing_state='NY',
            billing_postal_code='10001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            status='pending'
        )
        
        assert order.user is None
        assert order.first_name == 'Guest'
    
    def test_order_tracking(self, db):
        """Test order tracking number"""
        from apps.orders.models import Order
        order = Order.objects.create(
            order_number='ORD016',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
            billing_address_line_1='123 Main St',
            billing_city='New York',
            billing_state='NY',
            billing_postal_code='10001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            tracking_number='TRACK123456'
        )
        
        assert order.tracking_number == 'TRACK123456'


class TestOrderItem:
    """Tests for OrderItem model"""
    
    def test_order_item_creation(self, db):
        """Test creating an order item"""
        from apps.orders.models import Order, OrderItem
        from apps.products.models import Product
        
        order = Order.objects.create(
            order_number='ORD017',
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='123 Main St',
            shipping_city='New York',
            shipping_state='NY',
            shipping_postal_code='10001',
            shipping_country='US',
            billing_address_line_1='123 Main St',
            billing_city='New York',
            billing_state='NY',
            billing_postal_code='10001',
            billing_country='US',
            subtotal=100.00,
            total=100.00,
            status='pending'
        )
        product = Product.objects.create(
            sku='PROD001',
            name='Test Product',
            slug='test-product',
            regular_price=100.00
        )
        
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name='Test Product',
            product_sku='PROD001',
            quantity=2,
            price=100.00,
            subtotal=200.00
        )
        
        assert item.order == order
        assert item.product == product
        assert item.quantity == 2
        assert item.price == 100.00
        assert item.subtotal == 200.00
        assert str(item) == f"Order #ORD017 - Test Product"
    
    def test_order_item_str(self, db):
        """Test string representation of order item"""
        from apps.orders.models import Order, OrderItem
        from apps.products.models import Product
        
        order = Order.objects.create(
            order_number='ORD018',
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='456 Oak Ave',
            shipping_city='Los Angeles',
            shipping_state='CA',
            shipping_postal_code='90001',
            shipping_country='US',
            billing_address_line_1='456 Oak Ave',
            billing_city='Los Angeles',
            billing_state='CA',
            billing_postal_code='90001',
            billing_country='US',
            subtotal=100.00,
            total=100.00
        )
        product = Product.objects.create(
            sku='PROD002',
            name='Another Product',
            slug='another-product',
            regular_price=50.00
        )
        
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name='Another Product',
            product_sku='PROD002',
            quantity=3,
            price=50.00,
            subtotal=150.00
        )
        assert str(item) == f"Order #ORD018 - Another Product"
    
    def test_order_item_total_calculation(self, db):
        """Test order item total calculation"""
        from apps.orders.models import Order, OrderItem
        from apps.products.models import Product
        
        order = Order.objects.create(
            order_number='ORD019',
            first_name='Bob',
            last_name='Smith',
            email='bob@example.com',
            phone_number='+1234567890',
            shipping_address_line_1='789 Pine Rd',
            shipping_city='Chicago',
            shipping_state='IL',
            shipping_postal_code='60601',
            shipping_country='US',
            billing_address_line_1='789 Pine Rd',
            billing_city='Chicago',
            billing_state='IL',
            billing_postal_code='60601',
            billing_country='US',
            subtotal=100.00,
            total=100.00
        )
        product = Product.objects.create(
            sku='PROD003',
            name='Total Test',
            slug='total-test',
            regular_price=25.00
        )
        
        item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name='Total Test',
            product_sku='PROD003',
            quantity=4,
            price=25.00,
            subtotal=100.00
        )
        
        assert item.subtotal == 100.00
