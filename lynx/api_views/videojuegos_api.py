# videojuegos_api.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from lynx.models import Videojuego
from lynx.serializers import VideojuegoSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser

#=================================================================
# VIEWSET VIDEOJUEGO (CRUD COMPLETO)
#=================================================================
class VideojuegoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar videojuegos (CRUD).
    - Listar, crear, editar, eliminar.
    - Usuarios normales pueden ver.
    - Solo ADMIN o DISTR pueden crear, editar, eliminar.
    """
    queryset = Videojuego.objects.all()
    serializer_class = VideojuegoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CustomIsAdminOrDist()]
        return [permissions.AllowAny()]  # Cualquiera puede ver juegos


#=================================================================
# PERMISOS PERSONALIZADOS PARA ADMIN Y DIST SOLO EN MODIFICACIÓN
#=================================================================
from rest_framework.permissions import BasePermission

class CustomIsAdminOrDist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['ADMIN', 'DIST']
