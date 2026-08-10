"""
API Documentation Package
Swagger/OpenAPI documentation for the API
"""

from .swagger import get_swagger_view
from .schemas import (
    get_core_schemas,
    get_accounts_schemas,
    get_products_schemas,
    get_cart_schemas,
    get_orders_schemas,
    get_payments_schemas,
    get_shipping_schemas,
    get_inventory_schemas,
    get_discounts_schemas,
    get_reviews_schemas,
    get_support_schemas,
    get_blog_schemas,
    get_ads_schemas,
)

__all__ = [
    'get_swagger_view',
    'get_core_schemas',
    'get_accounts_schemas',
    'get_products_schemas',
    'get_cart_schemas',
    'get_orders_schemas',
    'get_payments_schemas',
    'get_shipping_schemas',
    'get_inventory_schemas',
    'get_discounts_schemas',
    'get_reviews_schemas',
    'get_support_schemas',
    'get_blog_schemas',
    'get_ads_schemas',
]
