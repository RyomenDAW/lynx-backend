
from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Permiso personalizado para usuarios con rol ADMIN.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'rol', None) == 'ADMIN')
