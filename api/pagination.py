"""
Custom Pagination Classes
"""

from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom page number pagination with customizable settings
    """
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page': self.page.number,
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large result sets
    """
    
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for small result sets
    """
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CustomCursorPagination(CursorPagination):
    """
    Custom cursor pagination for infinite scroll
    """
    
    page_size = 20
    max_page_size = 100
    ordering = '-created_at'
    cursor_query_param = 'cursor'
    
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'results': data
        })
