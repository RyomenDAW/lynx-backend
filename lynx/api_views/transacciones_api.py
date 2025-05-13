# transacciones_api.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from lynx.models import TransaccionItem, Item
from lynx.serializers import TransaccionItemSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

#=================================================================
# VIEWSET TRANSACCIONES DE ÍTEMS ENTRE USUARIOS
#=================================================================
class TransaccionItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar transacciones de items entre usuarios.
    - Listar, ver detalle.
    - Crear transacción (VENTA).
    - Solo el vendedor o comprador pueden ver la transacción.
    """
    serializer_class = TransaccionItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return TransaccionItem.objects.filter(
            vendedor=user
        ) | TransaccionItem.objects.filter(
            comprador=user
        )

    def perform_create(self, serializer):
        item_id = self.request.data.get('item')
        precio = self.request.data.get('precio')
        tipo_transaccion = self.request.data.get('tipo_transaccion')

        item = get_object_or_404(Item, id=item_id)
        comprador = self.request.user

        # Validación básica (puedes añadir más reglas según tu lógica)
        if not precio or float(precio) <= 0:
            raise ValueError("Precio inválido.")

        vendedor = item.juego.desarrollador if item.juego else None  # Aquí puedes definir la lógica de vendedor real si tienes control de ownership
        if not vendedor:
            raise ValueError("No se puede determinar el vendedor.")

        serializer.save(vendedor=vendedor, comprador=comprador, item=item, tipo_transaccion=tipo_transaccion)
