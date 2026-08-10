"""
API Permissions Package
Custom permission classes
"""

from .base_permissions import (
    IsOwner,
    IsStaffOrReadOnly,
    IsSuperuser,
    HasPermission,
)

__all__ = [
    'IsOwner',
    'IsStaffOrReadOnly',
    'IsSuperuser',
    'HasPermission',
]
