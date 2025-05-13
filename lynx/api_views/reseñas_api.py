# reseñas_api.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from lynx.models import Reseña, Videojuego, Biblioteca
from lynx.serializers import ReseñaSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

#=================================================================
# VIEWSET RESEÑAS (CRUD)
#=================================================================
class ReseñaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reseñas.
    - Crear solo si el usuario posee el juego.
    - Editar y eliminar solo la propia reseña.
    - Listado público.
    """
    serializer_class = ReseñaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Permitir ver todas las reseñas de un juego
        juego_id = self.request.query_params.get('juego_id')
        if juego_id:
            return Reseña.objects.filter(juego_id=juego_id).order_by('-fecha')
        return Reseña.objects.all().order_by('-fecha')

    def perform_create(self, serializer):
        juego_id = self.request.data.get('juego')
        juego = get_object_or_404(Videojuego, id=juego_id)

        # Solo si el usuario posee el juego
        if not Biblioteca.objects.filter(usuario=self.request.user, juego=juego).exists():
            raise PermissionError("No puedes reseñar un juego que no posees.")

        # Solo si no ha hecho una reseña previa
        if Reseña.objects.filter(usuario=self.request.user, juego=juego).exists():
            raise PermissionError("Ya has reseñado este juego.")

        serializer.save(usuario=self.request.user, juego=juego)

    def perform_update(self, serializer):
        # Solo el dueño puede editar
        if serializer.instance.usuario != self.request.user:
            raise PermissionError("No puedes editar esta reseña.")
        serializer.save()

    def perform_destroy(self, instance):
        # Solo el dueño puede eliminar
        if instance.usuario != self.request.user:
            raise PermissionError("No puedes eliminar esta reseña.")
        instance.delete()
