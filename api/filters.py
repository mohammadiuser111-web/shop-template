"""
Custom Filter Classes
"""

from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend


class RangeFilter(filters.NumericFilter):
    """
    Custom filter for numeric range filtering
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', 'range')
        super().__init__(*args, **kwargs)


class DateRangeFilter(filters.DateFilter):
    """
    Custom filter for date range filtering
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', 'range')
        super().__init__(*args, **kwargs)


class MultiValueFilter(filters.BaseCSVFilter):
    """
    Custom filter for multiple values in a single field
    """
    
    def filter(self, qs, value):
        if not value:
            return qs
        values = value.split(',')
        return qs.filter(**{f'{self.field_name}__in': values})


class SearchFilterBackend(BaseFilterBackend):
    """
    Custom search filter backend
    """
    
    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', [])
        search_param = getattr(view, 'search_param', 'search')
        
        if not search_fields or search_param not in request.query_params:
            return queryset
        
        search_value = request.query_params[search_param]
        if not search_value:
            return queryset
        
        from django.db.models import Q
        queries = []
        for field in search_fields:
            queries.append(Q(**{f'{field}__icontains': search_value}))
        
        if queries:
            queryset = queryset.filter(*queries)
        
        return queryset
