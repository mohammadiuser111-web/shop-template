"""
Permissions for ads API.
"""
from rest_framework import permissions


class IsAdAdminOrReadOnly(permissions.BasePermission):
    """Allow read-only access for all, but only admins can modify."""
    
    def has_permission(self, request, view):
        """Check permission for view."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAdSlotOwnerOrAdmin(permissions.BasePermission):
    """Allow access only to owner or admin."""
    
    def has_object_permission(self, request, view, obj):
        """Check object permission."""
        if request.user and request.user.is_staff:
            return True
        return obj.created_by == request.user


class CanViewAdStats(permissions.BasePermission):
    """Allow viewing ad statistics for admins only."""
    
    def has_permission(self, request, view):
        """Check permission."""
        return request.user and request.user.is_staff


class CanTrackAds(permissions.BasePermission):
    """Allow tracking for all users."""
    
    def has_permission(self, request, view):
        """Check permission."""
        return True
