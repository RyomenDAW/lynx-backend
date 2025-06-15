from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from lynx.models import ItemEnVenta, Item, InventarioItem
from lynx.serializers import ItemEnVentaSerializer
from rest_framework.permissions import IsAuthenticated

#=================================================================
# VIEWSET PARA PONER ÍTEMS EN VENTA
#=================================================================
class PonerEnVentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para poner ítems en venta:
    - VER ÍTEMS EN VENTA PROPIOS (list)
    - PONER EN VENTA (POST → /poner_en_venta/)
    - ELIMINAR ANUNCIO Y DEVOLVER ÍTEM AL INVENTARIO (DELETE)
    """
    serializer_class = ItemEnVentaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # CADA USUARIO SOLO VE SUS ÍTEMS EN VENTA
        return ItemEnVenta.objects.filter(vendedor=self.request.user)

    #=================================================================
    # ACCIÓN PERSONALIZADA → PONER ÍTEM EN VENTA
    # POST → /api/marketplace-venta/poner_en_venta/
    #=================================================================
    @action(detail=False, methods=['post'], url_path='poner_en_venta')
    def poner_en_venta(self, request):
        item_id = request.data.get('item_id')
        precio = request.data.get('precio')

        if not item_id or not precio:
            return Response({'error': 'Datos incompletos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = Item.objects.get(id=item_id)
            precio = float(precio)
            if precio <= 0:
                raise ValueError
        except (Item.DoesNotExist, ValueError):
            return Response({'error': 'Datos inválidos.'}, status=status.HTTP_400_BAD_REQUEST)

        # VERIFICAR QUE EL USUARIO TIENE EL ÍTEM EN INVENTARIO
        inventario_entry = InventarioItem.objects.filter(usuario=request.user, item=item).first()
        if not inventario_entry or inventario_entry.cantidad <= 0:
            return Response({'error': 'No tienes este ítem en tu inventario.'}, status=status.HTTP_400_BAD_REQUEST)

        # DESCONTAR 1 UNIDAD DEL INVENTARIO
        inventario_entry.cantidad -= 1
        if inventario_entry.cantidad == 0:
            inventario_entry.delete()
        else:
            inventario_entry.save()

        # CREAR ITEM EN VENTA
        ItemEnVenta.objects.create(
            vendedor=request.user,
            item=item,
            precio=precio
        )

        return Response({'success': f'Ítem "{item.nombre}" puesto en venta por {precio} €.'}, status=status.HTTP_201_CREATED)

    #=================================================================
    # SOBRESCRIBIR DELETE → DEVOLVER ÍTEM AL INVENTARIO DEL USUARIO
    #=================================================================
    def destroy(self, request, *args, **kwargs):
        item_en_venta = self.get_object()
        item = item_en_venta.item
        usuario = item_en_venta.vendedor

        # DEVOLVER EL ÍTEM AL INVENTARIO DEL USUARIO
        inventario, creado = InventarioItem.objects.get_or_create(
            usuario=usuario,
            item=item,
            defaults={'cantidad': 0}
        )
        inventario.cantidad += 1
        inventario.save()

        # ELIMINAR EL ANUNCIO DE LA TIENDA
        item_en_venta.delete()

        return Response({'success': 'Ítem eliminado del marketplace y devuelto al inventario.'}, status=status.HTTP_200_OK)
