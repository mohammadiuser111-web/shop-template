"""
Tests for Inventory API endpoints.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.inventory.models import Warehouse, Inventory, Supplier, PurchaseOrder
from apps.products.models import Product, Category

User = get_user_model()


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Create admin authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        phone_number='09123456789',
        email='test@test.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return User.objects.create_user(
        phone_number='09123456788',
        email='admin@test.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def category(db):
    """Create a test category."""
    return Category.objects.create(
        name='Test Category',
        slug='test-category'
    )


@pytest.fixture
def product(db, category):
    """Create a test product."""
    return Product.objects.create(
        name='Test Product',
        slug='test-product',
        category=category,
        price=100000,
        sku='TEST-SKU-001'
    )


@pytest.fixture
def warehouse(db):
    """Create a test warehouse."""
    return Warehouse.objects.create(
        name='Main Warehouse',
        code='WH-001',
        address='123 Warehouse Street',
        city='Tehran',
        state='Tehran',
        postal_code='12345',
        country='Iran',
        phone='02112345678',
        is_active=True
    )


@pytest.fixture
def inventory(db, product, warehouse):
    """Create a test inventory record."""
    return Inventory.objects.create(
        product=product,
        warehouse=warehouse,
        quantity=100,
        reserved_quantity=0,
        low_stock_threshold=10
    )


@pytest.fixture
def supplier(db):
    """Create a test supplier."""
    return Supplier.objects.create(
        name='Test Supplier',
        contact_person='John Doe',
        email='supplier@test.com',
        phone='09123456787',
        address='123 Supplier Street',
        city='Tehran',
        state='Tehran',
        postal_code='12345',
        country='Iran',
        is_active=True
    )


@pytest.fixture
def purchase_order(db, warehouse, supplier):
    """Create a test purchase order."""
    return PurchaseOrder.objects.create(
        po_number='PO-TEST-001',
        warehouse=warehouse,
        supplier=supplier,
        status='pending',
        subtotal=500000,
        tax_amount=0,
        total_amount=500000,
        currency='IRR',
        expected_delivery_date='2026-09-01'
    )


class TestWarehouseAPI:
    """Test Warehouse endpoints."""
    
    def test_list_warehouses_admin(self, admin_client, warehouse):
        """Test listing warehouses as admin."""
        url = reverse('api_v1:inventory_api:api-warehouses-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_warehouse_admin(self, admin_client):
        """Test creating a warehouse as admin."""
        url = reverse('api_v1:inventory_api:api-warehouses-create')
        data = {
            'name': 'Test Warehouse',
            'code': 'WH-002',
            'address': '456 Warehouse Street',
            'city': 'Tehran',
            'state': 'Tehran',
            'postal_code': '67890',
            'country': 'Iran',
            'phone': '02198765432',
            'is_active': True
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']
    
    def test_create_warehouse_unauthorized(self, authenticated_client):
        """Test creating a warehouse as non-admin."""
        url = reverse('api_v1:inventory_api:api-warehouses-create')
        data = {}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestInventoryAPI:
    """Test Inventory endpoints."""
    
    def test_list_inventory_admin(self, admin_client, inventory):
        """Test listing inventory as admin."""
        url = reverse('api_v1:inventory_api:api-inventory-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_get_inventory_by_product(self, api_client, inventory, product):
        """Test getting inventory by product."""
        url = reverse('api_v1:inventory_api:api-inventory-product', kwargs={'product_id': product.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_update_inventory_admin(self, admin_client, inventory):
        """Test updating inventory as admin."""
        url = reverse('api_v1:inventory_api:api-inventory-update', kwargs={'pk': inventory.id})
        data = {'quantity': 150}
        response = admin_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['quantity'] == 150
    
    def test_check_stock(self, api_client, inventory, product):
        """Test checking stock availability."""
        url = reverse('api_v1:inventory_api:api-inventory-check-stock')
        data = {
            'product_id': product.id,
            'quantity': 5
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['in_stock'] == True
    
    def test_check_low_stock(self, api_client, inventory, product):
        """Test checking for low stock."""
        url = reverse('api_v1:inventory_api:api-inventory-low-stock')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK


class TestSupplierAPI:
    """Test Supplier endpoints."""
    
    def test_list_suppliers_admin(self, admin_client, supplier):
        """Test listing suppliers as admin."""
        url = reverse('api_v1:inventory_api:api-suppliers-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_supplier_admin(self, admin_client):
        """Test creating a supplier as admin."""
        url = reverse('api_v1:inventory_api:api-suppliers-create')
        data = {
            'name': 'New Supplier',
            'contact_person': 'Jane Doe',
            'email': 'new@supplier.com',
            'phone': '09123456786',
            'is_active': True
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == data['name']


class TestPurchaseOrderAPI:
    """Test Purchase Order endpoints."""
    
    def test_list_purchase_orders_admin(self, admin_client, purchase_order):
        """Test listing purchase orders as admin."""
        url = reverse('api_v1:inventory_api:api-purchase-orders-list')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_create_purchase_order_admin(self, admin_client, warehouse, supplier):
        """Test creating a purchase order as admin."""
        url = reverse('api_v1:inventory_api:api-purchase-orders-create')
        data = {
            'warehouse': warehouse.id,
            'supplier': supplier.id,
            'status': 'pending',
            'expected_delivery_date': '2026-09-01',
            'notes': 'Test purchase order'
        }
        response = admin_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'po_number' in response.data
    
    def test_receive_purchase_order_admin(self, admin_client, purchase_order):
        """Test receiving a purchase order as admin."""
        url = reverse('api_v1:inventory_api:api-purchase-orders-receive', kwargs={'pk': purchase_order.id})
        response = admin_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'received'


class TestInventoryStatisticsAPI:
    """Test Inventory statistics endpoint."""
    
    def test_get_statistics_admin(self, admin_client, warehouse, inventory):
        """Test getting inventory statistics as admin."""
        url = reverse('api_v1:inventory_api:api-inventory-statistics')
        response = admin_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_products' in response.data
        assert 'total_warehouses' in response.data
    
    def test_get_statistics_unauthorized(self, authenticated_client):
        """Test getting inventory statistics as non-admin."""
        url = reverse('api_v1:inventory_api:api-inventory-statistics')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
