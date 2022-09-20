from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Полный доступ автору или только чтение для остальных"""
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
