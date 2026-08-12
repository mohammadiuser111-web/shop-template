"""
Pagination for ads API.
"""
from rest_framework.pagination import PageNumberPagination


class AdPagination(PageNumberPagination):
    """Custom pagination for ads API."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdSlotPagination(PageNumberPagination):
    """Custom pagination for ad slots API."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class AdImpressionPagination(PageNumberPagination):
    """Custom pagination for ad impressions API."""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class AdClickPagination(PageNumberPagination):
    """Custom pagination for ad clicks API."""
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
