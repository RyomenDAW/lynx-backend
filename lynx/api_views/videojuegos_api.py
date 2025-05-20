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
    queryset = Videojuego.objects.all()
    serializer_class = VideojuegoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), CustomIsAdminOrDist()]
        return [permissions.AllowAny()]

    def create(self, request, *args, **kwargs):
        print("📦 DATOS RECIBIDOS EN EL BACKEND:", request.data.get("imagen_portada_base64")[:100])  # Primeros 100 chars
        return super().create(request, *args, **kwargs)

#=================================================================
# PERMISOS PERSONALIZADOS PARA ADMIN Y DIST SOLO EN MODIFICACIÓN
#=================================================================
from rest_framework.permissions import BasePermission

class CustomIsAdminOrDist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['ADMIN', 'DIST']
