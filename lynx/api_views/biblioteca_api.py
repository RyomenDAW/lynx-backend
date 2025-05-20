# biblioteca_api.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from lynx.models import Biblioteca, Videojuego
from lynx.serializers import BibliotecaSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

#=================================================================
# VIEWSET BIBLIOTECA DEL USUARIO (Listar, comprar, eliminar, favorito)
#=================================================================
class BibliotecaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar la biblioteca del usuario.
    - Solo muestra y modifica la biblioteca del usuario autenticado.
    """
    serializer_class = BibliotecaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Solo la biblioteca del usuario autenticado
        return Biblioteca.objects.filter(usuario=self.request.user)

    #=============================================================
    # Acción personalizada para comprar juego (POST /api/biblioteca/comprar/)
    #=============================================================
    @action(detail=False, methods=['post'])
    def comprar(self, request):
        juego_id = request.data.get('juego_id')
        juego = get_object_or_404(Videojuego, id=juego_id)

        # Comprobamos si ya lo tiene
        if Biblioteca.objects.filter(usuario=request.user, juego=juego).exists():
            return Response({'error': 'Ya posees este juego.'}, status=status.HTTP_400_BAD_REQUEST)

        # Restar saldo
        request.user.saldo_virtual -= juego.precio
        request.user.save()

        
        Biblioteca.objects.create(usuario=request.user, juego=juego)
        return Response({'ok': True, 'mensaje': 'Juego añadido a la biblioteca.'})

    #=============================================================
    # Acción personalizada para marcar favorito (POST /api/biblioteca/{id}/favorito/)
    #=============================================================
    @action(detail=True, methods=['post'])
    def favorito(self, request, pk=None):
        registro = get_object_or_404(Biblioteca, id=pk, usuario=request.user)
        registro.favorito = not registro.favorito
        registro.save()
        return Response({'ok': True, 'favorito': registro.favorito})


    # PATCH /api/biblioteca/{id}/tiempo/
    @action(detail=True, methods=['patch'])
    def tiempo(self, request, pk=None):
        registro = get_object_or_404(Biblioteca, id=pk, usuario=request.user)
        minutos = request.data.get('minutos', 0)
        try:
            minutos = int(minutos)
        except:
            return Response({'error': 'Minutos inválidos.'}, status=400)

        registro.tiempo_jugado = minutos
        registro.save()
        return Response({'ok': True, 'tiempo_jugado': registro.tiempo_jugado})
