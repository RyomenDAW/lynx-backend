from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from lynx.models import Amistad, Usuario
from lynx.serializers import AmistadSerializer, UsuarioSerializer
from django.db.models import Q

class SocialViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='amigos')
    def amigos(self, request):
        usuario = request.user
        amistades = Amistad.objects.filter(
            Q(solicitante=usuario) | Q(receptor=usuario),
            estado='ACEPTADA'
        )
        amigos = [
            a.receptor if a.solicitante == usuario else a.solicitante
            for a in amistades
        ]
        serializer = UsuarioSerializer(amigos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='solicitudes')
    def solicitudes(self, request):
        solicitudes = Amistad.objects.filter(
            receptor=request.user,
            estado='PENDIENTE'
        )
        serializer = AmistadSerializer(solicitudes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='buscar')
    def buscar(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response([])
        usuarios = Usuario.objects.filter(username__icontains=query).exclude(id=request.user.id)
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='solicitar')
    def solicitar(self, request):
        receptor_id = request.data.get('receptor_id')
        receptor = Usuario.objects.filter(id=receptor_id).first()
        if not receptor:
            return Response({'error': 'Usuario no encontrado'}, status=404)
        if Amistad.objects.filter(solicitante=request.user, receptor=receptor).exists():
            return Response({'error': 'Ya has enviado solicitud'}, status=400)

        amistad = Amistad.objects.create(solicitante=request.user, receptor=receptor, estado='PENDIENTE')
        return Response({'ok': True, 'id': amistad.id})

    @action(detail=True, methods=['post'], url_path='aceptar')
    def aceptar(self, request, pk=None):
        amistad = Amistad.objects.filter(id=pk, receptor=request.user, estado='PENDIENTE').first()
        if not amistad:
            return Response({'error': 'Solicitud no válida'}, status=400)
        amistad.estado = 'ACEPTADA'
        amistad.save()
        return Response({'ok': True})


    @action(detail=True, methods=['post'], url_path='rechazar')
    def rechazar(self, request, pk=None):
        amistad = Amistad.objects.filter(id=pk, receptor=request.user, estado='PENDIENTE').first()
        if not amistad:
            return Response({'error': 'Solicitud no válida'}, status=400)
        amistad.delete()
        return Response({'ok': True})


    def destroy(self, request, pk=None):
        amistad = Amistad.objects.filter(
            Q(solicitante=request.user, receptor__id=pk) |
            Q(receptor=request.user, solicitante__id=pk),
            estado='ACEPTADA'
        ).first()
        if not amistad:
            return Response({'error': 'Amistad no encontrada'}, status=404)
        amistad.delete()
        return Response({'ok': True})
