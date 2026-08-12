"""
Unit tests for Shipping application models.
Tests ShippingMethod, ShippingZone, ShippingClass models.
"""

import pytest

pytestmark = pytest.mark.django_db


class TestShippingZone:
    """Tests for ShippingZone model"""
    
    def test_shipping_zone_creation(self, db):
        """Test creating a shipping zone"""
        from apps.shipping.models import ShippingZone
        zone = ShippingZone.objects.create(
            name='Domestic',
            description='Domestic shipping zone'
        )
        
        assert zone.name == 'Domestic'
        assert zone.description == 'Domestic shipping zone'
        assert str(zone) == 'Domestic'
    
    def test_shipping_zone_str(self, db):
        """Test string representation of shipping zone"""
        from apps.shipping.models import ShippingZone
        zone = ShippingZone.objects.create(name='International')
        assert str(zone) == 'International'
    
    def test_shipping_zone_name(self, db):
        """Test shipping zone name"""
        from apps.shipping.models import ShippingZone
        zone = ShippingZone.objects.create(name='Local')
        assert zone.name == 'Local'
    
    def test_shipping_zone_created_at(self, db):
        """Test shipping zone created_at timestamp"""
        from apps.shipping.models import ShippingZone
        zone = ShippingZone.objects.create(name='Time Zone')
        assert zone.created_at is not None
    
    def test_shipping_zone_updated_at(self, db):
        """Test shipping zone updated_at timestamp"""
        from apps.shipping.models import ShippingZone
        zone = ShippingZone.objects.create(name='Updated Zone')
        assert zone.updated_at is not None


class TestShippingMethod:
    """Tests for ShippingMethod model"""
    
    def test_shipping_method_creation(self, db):
        """Test creating a shipping method"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Standard Zone')
        method = ShippingMethod.objects.create(
            name='Standard Shipping',
            slug='standard-shipping',
            description='Standard shipping method',
            zone=zone,
            pricing_type='fixed',
            base_price=5.00
        )
        
        assert method.name == 'Standard Shipping'
        assert method.slug == 'standard-shipping'
        assert method.description == 'Standard shipping method'
        assert method.pricing_type == 'fixed'
        assert method.base_price == 5.00
        assert str(method) == 'Standard Shipping'
    
    def test_shipping_method_str(self, db):
        """Test string representation of shipping method"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Express Zone')
        method = ShippingMethod.objects.create(
            name='Express Shipping',
            slug='express-shipping',
            zone=zone,
            base_price=10.00
        )
        assert str(method) == 'Express Shipping'
    
    def test_shipping_method_pricing_types(self, db):
        """Test different shipping pricing types"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Pricing Zone')
        
        fixed = ShippingMethod.objects.create(
            name='Fixed Cost',
            slug='fixed-cost',
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
    
    def test_shipping_method_costs(self, db):
        """Test shipping method cost fields"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Cost Zone')
        method = ShippingMethod.objects.create(
            name='Cost Test',
            slug='cost-test',
            zone=zone,
            pricing_type='fixed',
            base_price=8.00,
            price_per_item=1.00,
            price_per_kg=0.50
        )
        
        assert method.base_price == 8.00
        assert method.price_per_item == 1.00
        assert method.price_per_kg == 0.50
    
    def test_shipping_method_created_at(self, db):
        """Test shipping method created_at timestamp"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Time Zone')
        method = ShippingMethod.objects.create(
            name='Time Method',
            slug='time-method',
            zone=zone,
            base_price=10.00
        )
        assert method.created_at is not None
    
    def test_shipping_method_updated_at(self, db):
        """Test shipping method updated_at timestamp"""
        from apps.shipping.models import ShippingMethod, ShippingZone
        zone = ShippingZone.objects.create(name='Updated Zone')
        method = ShippingMethod.objects.create(
            name='Updated Method',
            slug='updated-method',
            zone=zone,
            base_price=10.00
        )
        assert method.updated_at is not None


class TestShippingClass:
    """Tests for ShippingClass model"""
    
    def test_shipping_class_creation(self, db):
        """Test creating a shipping class"""
        from apps.shipping.models import ShippingClass
        shipping_class = ShippingClass.objects.create(
            name='Standard',
            slug='standard',
            description='Standard shipping class for regular products'
        )
        
        assert shipping_class.name == 'Standard'
        assert shipping_class.slug == 'standard'
        assert shipping_class.description == 'Standard shipping class for regular products'
        assert str(shipping_class) == 'Standard'
    
    def test_shipping_class_str(self, db):
        """Test string representation of shipping class"""
        from apps.shipping.models import ShippingClass
        shipping_class = ShippingClass.objects.create(
            name='Express',
            slug='express'
        )
        assert str(shipping_class) == 'Express'
    
    def test_shipping_class_name(self, db):
        """Test shipping class name"""
        from apps.shipping.models import ShippingClass
        shipping_class = ShippingClass.objects.create(
            name='Overnight',
            slug='overnight'
        )
        assert shipping_class.name == 'Overnight'
    
    def test_shipping_class_created_at(self, db):
        """Test shipping class created_at timestamp"""
        from apps.shipping.models import ShippingClass
        shipping_class = ShippingClass.objects.create(
            name='Time Class',
            slug='time-class'
        )
        assert shipping_class.created_at is not None
    
    def test_shipping_class_updated_at(self, db):
        """Test shipping class updated_at timestamp"""
        from apps.shipping.models import ShippingClass
        shipping_class = ShippingClass.objects.create(
            name='Updated Class',
            slug='updated-class'
        )
        assert shipping_class.updated_at is not None
