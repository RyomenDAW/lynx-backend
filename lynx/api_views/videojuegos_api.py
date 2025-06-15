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
        # ✅ EVITA EL ERROR 500 SI NO SE ENVÍA imagen_portada_base64
        imagen = request.data.get("imagen_portada_base64")
        if imagen:
            print("📦 DATOS RECIBIDOS EN EL BACKEND (base64 truncado):", imagen[:100])
        else:
            print("📦 DATOS RECIBIDOS EN EL BACKEND: imagen_portada_base64 no recibido.")
        
        return super().create(request, *args, **kwargs)


#=================================================================
# PERMISOS PERSONALIZADOS PARA ADMIN Y DIST SOLO EN MODIFICACIÓN
#=================================================================
from rest_framework.permissions import BasePermission

class CustomIsAdminOrDist(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['ADMIN', 'DIST']
