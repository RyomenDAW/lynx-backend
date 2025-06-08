# lynx/api_views/inventario_api.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from lynx.models import InventarioItem, Item, Usuario, TransaccionItem
from lynx.serializers import InventarioItemSerializer
from rest_framework.permissions import IsAuthenticated, BasePermission

#=================================================================
# PERMISO PERSONALIZADO → SOLO ADMIN
#=================================================================
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'ADMIN'

#=================================================================
# VIEWSET INVENTARIO
#=================================================================
class InventarioItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el inventario:
    - LOS USUARIOS VEN SU PROPIO INVENTARIO.
    - ADMIN PUEDE VER TODOS LOS INVENTARIOS.
    - ADMIN PUEDE ASIGNAR ÍTEMS A USUARIOS.
    """
    serializer_class = InventarioItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.rol == 'ADMIN':
            return InventarioItem.objects.all()
        else:
            return InventarioItem.objects.filter(usuario=user)

    #=================================================================
    # ACCIÓN PERSONALIZADA → ADMIN ASIGNA ÍTEM A UN USUARIO (POR USERNAME)
    #=================================================================
    @action(detail=False, methods=['post'], url_path='asignar_item', permission_classes=[IsAuthenticated, IsAdmin])
    def asignar_item(self, request):
        username = request.data.get('username')
        item_id = request.data.get('item_id')
        cantidad = request.data.get('cantidad', 1)

        print("====== DEBUG BACKEND ======")
        print("USERNAME RECIBIDO:", username)
        print("ITEM_ID RECIBIDO:", item_id)
        print("CANTIDAD RECIBIDA:", cantidad)
        print("===========================")

        if not username or not item_id:
            return Response({'error': 'Datos incompletos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(username=username)
            print("USUARIO ENCONTRADO:", usuario.username)
            item = Item.objects.get(id=item_id)
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError
        except Usuario.DoesNotExist:
            return Response({'error': f'El usuario "{username}" no existe.'}, status=status.HTTP_404_NOT_FOUND)
        except Item.DoesNotExist:
            return Response({'error': 'Ítem no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        # ASIGNAR AL INVENTARIO
        inventario_entry, created = InventarioItem.objects.get_or_create(
            usuario=usuario,
            item=item,
            defaults={'cantidad': cantidad}
        )

        print("CREATED:", created)
        print("ANTES CANTIDAD:", inventario_entry.cantidad)

        if not created:
            inventario_entry.cantidad += cantidad
            inventario_entry.save()
            print("NUEVA CANTIDAD:", inventario_entry.cantidad)

        # REGISTRAR TRANSACCIÓN
        TransaccionItem.objects.create(
            vendedor=None,
            comprador=usuario,
            item=item,
            precio=0,
            tipo_transaccion='ASIGNACION_ADMIN'
        )

        print("======== TRANSACCIÓN CREADA ========")
        print("ITEM:", item.nombre)
        print("ASIGNADO A:", usuario.username)
        print("===================================")

        return Response({'success': f'Asignado {cantidad} x "{item.nombre}" a {usuario.username}.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='eliminar_item', permission_classes=[IsAuthenticated])
    def eliminar_item(self, request):
        user = request.user
        item_id = request.data.get('item_id')
        cantidad = int(request.data.get('cantidad', 0))

        if not item_id or cantidad <= 0:
            return Response({'error': 'Datos inválidos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({'error': 'Ítem no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            inventario_entry = InventarioItem.objects.get(usuario=user, item=item)
        except InventarioItem.DoesNotExist:
            return Response({'error': 'No tienes este ítem en tu inventario.'}, status=status.HTTP_404_NOT_FOUND)

        if inventario_entry.cantidad < cantidad:
            return Response({'error': 'No tienes suficientes ítems para eliminar.'}, status=status.HTTP_400_BAD_REQUEST)

        inventario_entry.cantidad -= cantidad

        if inventario_entry.cantidad == 0:
            inventario_entry.delete()
        else:
            inventario_entry.save()

        return Response({'success': f'Eliminado {cantidad} de "{item.nombre}".'}, status=status.HTTP_200_OK)
