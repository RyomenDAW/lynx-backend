# social_api.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from lynx.models import Amistad, Usuario
from lynx.serializers import AmistadSerializer, UsuarioSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

#=================================================================
# VIEWSET SOCIAL / AMIGOS / SOLICITUDES
#=================================================================
class SocialViewSet(viewsets.ViewSet):
    """
    ViewSet para gestionar amigos, solicitudes, rechazos.
    """
    permission_classes = [IsAuthenticated]

    #=============================================================
    # Listar amigos confirmados
    #=============================================================
    @action(detail=False, methods=['get'])
    def amigos(self, request):
        user = request.user
        amistades = Amistad.objects.filter(
            Q(solicitante=user) | Q(receptor=user),
            aceptada=True
        )
        amigos = [a.receptor if a.solicitante == user else a.solicitante for a in amistades]
        serializer = UsuarioSerializer(amigos, many=True)
        return Response(serializer.data)

    #=============================================================
    # Listar solicitudes recibidas
    #=============================================================
    @action(detail=False, methods=['get'])
    def solicitudes_recibidas(self, request):
        solicitudes = Amistad.objects.filter(receptor=request.user, aceptada=False)
        serializer = AmistadSerializer(solicitudes, many=True)
        return Response(serializer.data)

    #=============================================================
    # Buscar usuarios por nombre o email
    #=============================================================
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response([], status=status.HTTP_200_OK)

        resultados = Usuario.objects.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        ).exclude(id=request.user.id)

        serializer = UsuarioSerializer(resultados, many=True)
        return Response(serializer.data)

    #=============================================================
    # Enviar solicitud de amistad
    #=============================================================
    @action(detail=False, methods=['post'])
    def enviar_solicitud(self, request):
        receptor_id = request.data.get('receptor_id')
        receptor = get_object_or_404(Usuario, id=receptor_id)

        if receptor == request.user:
            return Response({'error': 'No puedes enviarte una solicitud a ti mismo.'}, status=status.HTTP_400_BAD_REQUEST)

        if Amistad.objects.filter(
            Q(solicitante=request.user, receptor=receptor) |
            Q(solicitante=receptor, receptor=request.user)
        ).exists():
            return Response({'error': 'Ya existe una solicitud o amistad.'}, status=status.HTTP_400_BAD_REQUEST)

        Amistad.objects.create(solicitante=request.user, receptor=receptor)
        return Response({'ok': True, 'mensaje': 'Solicitud enviada.'})

    #=============================================================
    # Aceptar solicitud
    #=============================================================
    @action(detail=True, methods=['post'])
    def aceptar(self, request, pk=None):
        solicitud = get_object_or_404(Amistad, id=pk, receptor=request.user)
        solicitud.aceptada = True
        solicitud.save()
        return Response({'ok': True, 'mensaje': 'Solicitud aceptada.'})

    #=============================================================
    # Rechazar solicitud
    #=============================================================
    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        solicitud = get_object_or_404(Amistad, id=pk, receptor=request.user)
        solicitud.delete()
        return Response({'ok': True, 'mensaje': 'Solicitud rechazada.'})

    #=============================================================
    # Eliminar amigo
    #=============================================================
    @action(detail=True, methods=['post'])
    def eliminar(self, request, pk=None):
        amigo = get_object_or_404(Usuario, pk=pk)
        Amistad.objects.filter(
            Q(solicitante=request.user, receptor=amigo) |
            Q(solicitante=amigo, receptor=request.user)
        ).delete()
        return Response({'ok': True, 'mensaje': 'Amigo eliminado.'})
