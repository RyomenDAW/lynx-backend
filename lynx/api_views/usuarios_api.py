# usuarios_api.py
from lynx.permissions import IsAdminRole
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from lynx.serializers import UsuarioSerializer
from rest_framework.permissions import IsAuthenticated

Usuario = get_user_model()

#=================================================================
# VIEWSET USUARIO (CRUD + PERSONALIZADAS)
#=================================================================
class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]  # Por defecto solo autenticados

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminRole()]
        return [IsAuthenticated()]

    #=============================================================
    # ENDPOINT PERSONALIZADO: PERFIL DEL USUARIO ACTUAL (GET /api/usuarios/perfil/)
    #=============================================================
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def perfil(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    #=============================================================
    # ENDPOINT PERSONALIZADO: MODIFICAR SALDO (POST /api/usuarios/añadir_saldo/)
    #=============================================================
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def añadir_saldo(self, request):
        try:
            cantidad = float(request.data.get('cantidad', 0))
            if cantidad <= 0:
                return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

            request.user.saldo_virtual += cantidad
            request.user.save()
            return Response({'ok': True, 'nuevo_saldo': float(request.user.saldo_virtual)})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
