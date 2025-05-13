# items_api.py

from rest_framework import viewsets, permissions
from lynx.models import Item
from lynx.serializers import ItemSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

#=================================================================
# VIEWSET ITEMS (CRUD COMPLETO)
#=================================================================
class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar items.
    - CRUD completo para ADMIN o DIST.
    - Visualización pública.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CustomIsAdminOrDist()]
        return [AllowAny()]  # Permitir visualizar a cualquiera


#=================================================================
# PERMISO PERSONALIZADO PARA ADMIN O DIST
#=================================================================
from rest_framework.permissions import BasePermission

class CustomIsAdminOrDist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['ADMIN', 'DIST']
