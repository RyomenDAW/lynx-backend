# lynx/api_views/transacciones_api.py

from rest_framework import viewsets, permissions
from lynx.models import TransaccionItem
from lynx.serializers import TransaccionItemSerializer
from rest_framework.permissions import IsAuthenticated, BasePermission

#=================================================================
# PERMISO PERSONALIZADO → SOLO ADMIN
#=================================================================
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'ADMIN'

#=================================================================
# VIEWSET TRANSACCIONES DE ÍTEMS
#=================================================================
class TransaccionItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver transacciones de ítems:
    - LOS USUARIOS VEN SUS PROPIAS (COMPRADOR O VENDEDOR).
    - ADMIN VE TODAS.
    """
    serializer_class = TransaccionItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.rol == 'ADMIN':
            return TransaccionItem.objects.all()
        else:
            return TransaccionItem.objects.filter(
                vendedor=user
            ) | TransaccionItem.objects.filter(
                comprador=user
            )
