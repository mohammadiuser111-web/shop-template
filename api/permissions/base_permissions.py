"""
Custom Permission Classes
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Permission to check if the user is the owner of the object
    """
    
    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'user') and obj.user == request.user


class IsStaffOrReadOnly(BasePermission):
    """
    Permission to allow read-only for everyone, but write only for staff
    """
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsSuperuser(BasePermission):
    """
    Permission to check if the user is a superuser
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class HasPermission(BasePermission):
    """
    Custom permission class to check for specific permissions
    """
    
    def __init__(self, permission_name):
        self.permission_name = permission_name
    
    def has_permission(self, request, view):
        return request.user and request.user.has_perm(self.permission_name)
