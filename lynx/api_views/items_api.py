# lynx/api_views/items_api.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from lynx.models import Item
from lynx.serializers import ItemSerializer

#=================================================================
# PERMISO PERSONALIZADO → SOLO ADMIN
#=================================================================
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'ADMIN'

#=================================================================
# VIEWSET ITEMS (CRUD CONTROLADO)
#=================================================================
class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar ítems:
    - SOLO ADMIN PUEDE CREAR / EDITAR / BORRAR.
    - CUALQUIERA PUEDE VER (list/retrieve).
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsAdmin]
        else:  # list / retrieve
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
