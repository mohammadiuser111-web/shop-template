"""
API URLs for Inventory app.
"""
from django.urls import path
from .views import (
    # Warehouse views
    WarehouseListAPIView, WarehouseRetrieveAPIView,
    WarehouseCreateAPIView, WarehouseUpdateAPIView,
    WarehouseDestroyAPIView,
    # Inventory views
    InventoryListAPIView, InventoryRetrieveAPIView,
    InventoryCreateAPIView, InventoryUpdateAPIView,
    InventoryStockUpdateAPIView, InventoryBulkUpdateAPIView,
    # Inventory Movement views
    InventoryMovementListAPIView, InventoryMovementRetrieveAPIView,
    # Stock Alert views
    StockAlertListAPIView, StockAlertRetrieveAPIView,
    # Supplier views
    SupplierListAPIView, SupplierRetrieveAPIView,
    SupplierCreateAPIView, SupplierUpdateAPIView,
    SupplierDestroyAPIView,
    # Purchase Order views
    PurchaseOrderListAPIView, PurchaseOrderRetrieveAPIView,
    PurchaseOrderCreateAPIView, PurchaseOrderUpdateAPIView,
    PurchaseOrderItemListAPIView, PurchaseOrderItemCreateAPIView,
    # Statistics and product inventory
    InventoryStatisticsAPIView, ProductInventoryAPIView
)

urlpatterns = [
    # Warehouses
    path('warehouses/', WarehouseListAPIView.as_view(), name='api-warehouses-list'),
    path('warehouses/create/', WarehouseCreateAPIView.as_view(), name='api-warehouses-create'),
    path('warehouses/<uuid:pk>/', WarehouseRetrieveAPIView.as_view(), name='api-warehouses-retrieve'),
    path('warehouses/<uuid:pk>/update/', WarehouseUpdateAPIView.as_view(), name='api-warehouses-update'),
    path('warehouses/<uuid:pk>/delete/', WarehouseDestroyAPIView.as_view(), name='api-warehouses-delete'),
    
    # Inventory
    path('inventory/', InventoryListAPIView.as_view(), name='api-inventory-list'),
    path('inventory/create/', InventoryCreateAPIView.as_view(), name='api-inventory-create'),
    path('inventory/<uuid:pk>/', InventoryRetrieveAPIView.as_view(), name='api-inventory-retrieve'),
    path('inventory/<uuid:pk>/update/', InventoryUpdateAPIView.as_view(), name='api-inventory-update'),
    path('inventory/stock-update/', InventoryStockUpdateAPIView.as_view(), name='api-inventory-stock-update'),
    path('inventory/bulk-update/', InventoryBulkUpdateAPIView.as_view(), name='api-inventory-bulk-update'),
    
    # Warehouse-specific inventory
    path('warehouses/<uuid:warehouse_id>/inventory/', InventoryListAPIView.as_view(), name='api-warehouse-inventory-list'),
    
    # Product-specific inventory
    path('products/<int:product_id>/inventory/', ProductInventoryAPIView.as_view(), name='api-product-inventory'),
    
    # Inventory Movements
    path('inventory/<uuid:inventory_id>/movements/', InventoryMovementListAPIView.as_view(), name='api-inventory-movements-list'),
    path('movements/<uuid:pk>/', InventoryMovementRetrieveAPIView.as_view(), name='api-inventory-movements-retrieve'),
    
    # Stock Alerts
    path('stock-alerts/', StockAlertListAPIView.as_view(), name='api-stock-alerts-list'),
    path('stock-alerts/<uuid:pk>/', StockAlertRetrieveAPIView.as_view(), name='api-stock-alerts-retrieve'),
    
    # Warehouse-specific stock alerts
    path('warehouses/<uuid:warehouse_id>/stock-alerts/', StockAlertListAPIView.as_view(), name='api-warehouse-stock-alerts-list'),
    
    # Suppliers
    path('suppliers/', SupplierListAPIView.as_view(), name='api-suppliers-list'),
    path('suppliers/create/', SupplierCreateAPIView.as_view(), name='api-suppliers-create'),
    path('suppliers/<uuid:pk>/', SupplierRetrieveAPIView.as_view(), name='api-suppliers-retrieve'),
    path('suppliers/<uuid:pk>/update/', SupplierUpdateAPIView.as_view(), name='api-suppliers-update'),
    path('suppliers/<uuid:pk>/delete/', SupplierDestroyAPIView.as_view(), name='api-suppliers-delete'),
    
    # Purchase Orders
    path('purchase-orders/', PurchaseOrderListAPIView.as_view(), name='api-purchase-orders-list'),
    path('purchase-orders/create/', PurchaseOrderCreateAPIView.as_view(), name='api-purchase-orders-create'),
    path('purchase-orders/<uuid:pk>/', PurchaseOrderRetrieveAPIView.as_view(), name='api-purchase-orders-retrieve'),
    path('purchase-orders/<uuid:pk>/update/', PurchaseOrderUpdateAPIView.as_view(), name='api-purchase-orders-update'),
    
    # Supplier-specific purchase orders
    path('suppliers/<uuid:supplier_id>/purchase-orders/', PurchaseOrderListAPIView.as_view(), name='api-supplier-purchase-orders-list'),
    
    # Warehouse-specific purchase orders
    path('warehouses/<uuid:warehouse_id>/purchase-orders/', PurchaseOrderListAPIView.as_view(), name='api-warehouse-purchase-orders-list'),
    
    # Purchase Order Items
    path('purchase-orders/<uuid:po_id>/items/', PurchaseOrderItemListAPIView.as_view(), name='api-purchase-order-items-list'),
    path('purchase-orders/<uuid:po_id>/items/create/', PurchaseOrderItemCreateAPIView.as_view(), name='api-purchase-order-items-create'),
    
    # Statistics
    path('statistics/', InventoryStatisticsAPIView.as_view(), name='api-inventory-statistics'),
]
