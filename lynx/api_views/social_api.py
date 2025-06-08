from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from lynx.models import Amistad, Usuario
# CORRECTO (como en usuarios_api.py)
from lynx.serializers import AmistadSerializer, UsuarioSerializer
from lynx.serializers import UsuarioSerializer, UsuarioPerfilSerializer
from django.db.models import Q
# IMPORTS
from lynx.models import Amistad, MensajePrivado, Usuario
from lynx.serializers import AmistadSerializer, UsuarioSerializer, MensajePrivadoSerializer

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

    @action(detail=True, methods=['get'], url_path='profile', permission_classes=[permissions.IsAuthenticated])
    def perfil_usuario(self, request, pk=None):
        usuario = Usuario.objects.filter(id=pk).first()
        if not usuario:
            return Response({'error': 'Usuario no encontrado'}, status=404)
        
        serializer = UsuarioPerfilSerializer(usuario)  # ✅ CAMBIO AQUI
        return Response(serializer.data)


    # CARGAR CHAT PRIVADO
    @action(detail=True, methods=['get'], url_path='chat')
    def chat_privado(self, request, pk=None):
        user = request.user
        try:
            amigo = Usuario.objects.get(id=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        # Solo puedes chatear con amigos
        es_amigo = Amistad.objects.filter(
            (Q(solicitante=user, receptor=amigo) | Q(receptor=user, solicitante=amigo)),
            estado='ACEPTADA'
        ).exists()

        if not es_amigo:
            return Response({'error': 'No eres amigo de este usuario.'}, status=403)

        mensajes = MensajePrivado.objects.filter(
            (Q(emisor=user, receptor=amigo) | Q(emisor=amigo, receptor=user))
        ).order_by('fecha_envio')

        serializer = MensajePrivadoSerializer(mensajes, many=True)
        return Response(serializer.data)

    # ENVIAR MENSAJE PRIVADO
    @action(detail=False, methods=['post'], url_path='enviar_mensaje')
    def enviar_mensaje(self, request):
        user = request.user
        receptor_id = request.data.get('receptor_id')
        contenido = request.data.get('contenido')

        if not receptor_id or not contenido:
            return Response({'error': 'Datos incompletos.'}, status=400)

        try:
            receptor = Usuario.objects.get(id=receptor_id)
        except Usuario.DoesNotExist:
            return Response({'error': 'Receptor no encontrado.'}, status=404)

        # Solo puedes enviar a amigos
        es_amigo = Amistad.objects.filter(
            (Q(solicitante=user, receptor=receptor) | Q(receptor=user, solicitante=receptor)),
            estado='ACEPTADA'
        ).exists()

        if not es_amigo:
            return Response({'error': 'No eres amigo de este usuario.'}, status=403)

        MensajePrivado.objects.create(
            emisor=user,
            receptor=receptor,
            contenido=contenido
        )

        return Response({'success': 'Mensaje enviado.'}, status=201)
