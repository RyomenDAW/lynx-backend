# lynx/api_views/marketplace_api.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from lynx.models import ItemEnVenta, InventarioItem, TransaccionItem
from lynx.serializers import ItemEnVentaSerializer, MarketplaceCompraSerializer
from rest_framework.permissions import IsAuthenticated

#=================================================================
# VIEWSET MARKETPLACE
#=================================================================
class MarketplaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para el Marketplace:
    - LISTAR ÍTEMS EN VENTA (GET)
    - COMPRAR ÍTEM (POST → /{id}/comprar/)
    """
    queryset = ItemEnVenta.objects.all()
    serializer_class = ItemEnVentaSerializer
    permission_classes = [IsAuthenticated]

    #=================================================================
    # ACCIÓN PERSONALIZADA → COMPRAR ÍTEM
    # POST → /api/marketplace/{id}/comprar/
    #=================================================================
    @action(detail=True, methods=['post'], url_path='comprar')
    def comprar(self, request, pk=None):
        try:
            item_en_venta = ItemEnVenta.objects.get(id=pk)
        except ItemEnVenta.DoesNotExist:
            return Response({'error': 'El ítem en venta no existe.'}, status=status.HTTP_404_NOT_FOUND)

        comprador = request.user
        vendedor = item_en_venta.vendedor
        precio = item_en_venta.precio

        # VALIDACIONES
        if comprador == vendedor:
            return Response({'error': 'No puedes comprar tu propio ítem.'}, status=status.HTTP_400_BAD_REQUEST)

        if comprador.saldo_virtual < precio:
            return Response({'error': 'Saldo insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

        # PROCESAR COMPRA
        comprador.saldo_virtual -= precio
        vendedor.saldo_virtual += precio

        comprador.save()
        vendedor.save()

        # ACTUALIZAR INVENTARIO DEL COMPRADOR
        inventario_entry, created = InventarioItem.objects.get_or_create(
            usuario=comprador,
            item=item_en_venta.item,
            defaults={'cantidad': 1}
        )
        if not created:
            inventario_entry.cantidad += 1
            inventario_entry.save()

        # REGISTRAR TRANSACCIÓN
        TransaccionItem.objects.create(
            vendedor=vendedor,
            comprador=comprador,
            item=item_en_venta.item,
            precio=precio,
            tipo_transaccion='VENTA'
        )

        # ELIMINAR EL ÍTEM DE LA TIENDA
        item_en_venta.delete()

        return Response({'success': 'Compra realizada correctamente.'}, status=status.HTTP_200_OK)
