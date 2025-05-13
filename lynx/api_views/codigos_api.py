# codigos_api.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from lynx.models import CodigoPromocional, Biblioteca
from lynx.serializers import CodigoPromocionalSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

#=================================================================
# VIEWSET CÓDIGOS PROMOCIONALES
#=================================================================
class CodigoPromocionalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar códigos promocionales.
    - CRUD completo solo para ADMIN o DIST.
    - Canjear accesible solo por usuarios autenticados.
    """
    queryset = CodigoPromocional.objects.all()
    serializer_class = CodigoPromocionalSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), CustomIsAdminOrDist()]
        return [permissions.IsAuthenticated()]

    #=============================================================
    # Acción personalizada para canjear código (POST /api/codigos/canjear/)
    #=============================================================
    @action(detail=False, methods=['post'])
    def canjear(self, request):
        codigo_texto = request.data.get('codigo', '').strip()
        if not codigo_texto:
            return Response({'error': 'Código no proporcionado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            codigo = CodigoPromocional.objects.get(codigo_texto=codigo_texto)
            if codigo.usado or codigo.usos_actuales >= codigo.usos_totales:
                return Response({'error': 'Este código ya ha sido usado al máximo.'}, status=status.HTTP_400_BAD_REQUEST)
            if codigo.fecha_expiracion < timezone.now().date():
                return Response({'error': 'Este código ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Añadir videojuego si aplica
            if codigo.videojuego:
                if not Biblioteca.objects.filter(usuario=request.user, juego=codigo.videojuego).exists():
                    Biblioteca.objects.create(usuario=request.user, juego=codigo.videojuego)

            # Añadir saldo si aplica
            if codigo.saldo_extra:
                request.user.saldo_virtual += codigo.saldo_extra
                request.user.save()

            # Actualizar uso
            codigo.usos_actuales += 1
            if codigo.usos_actuales >= codigo.usos_totales:
                codigo.usado = True
            codigo.usuario_ultimo = request.user
            codigo.save()

            return Response({'ok': True, 'mensaje': 'Código canjeado correctamente.'})
        except CodigoPromocional.DoesNotExist:
            return Response({'error': 'Código no válido.'}, status=status.HTTP_400_BAD_REQUEST)

#=================================================================
# PERMISO PERSONALIZADO PARA ADMIN O DIST
#=================================================================
from rest_framework.permissions import BasePermission

class CustomIsAdminOrDist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['ADMIN', 'DIST']
