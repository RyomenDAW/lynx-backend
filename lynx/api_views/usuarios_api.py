# usuarios_api.py
from lynx.permissions import IsAdminRole
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from lynx.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    #=============================================================
    # ENDPOINT PERSONALIZADO: PERFIL DEL USUARIO ACTUAL (GET /api/usuarios/perfil/)
    #=============================================================
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def perfil(self, request):
        usuario = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)

        if request.method == 'PATCH':
            serializer = self.get_serializer(usuario, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from lynx.models import Usuario

class RegisterView(APIView):
    def post(self, request):
        print("📥 DATOS RECIBIDOS EN BACKEND:", request.data)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario creado correctamente'}, status=status.HTTP_201_CREATED)
        print("❌ ERRORES:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from lynx.serializers import UsuarioSerializer

class UsuarioPerfilView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("🔍 HEADERS:", request.headers)
        print("🔍 Authorization:", request.headers.get("Authorization"))
        print("🔍 USER:", request.user)
        return Response({"mensaje": "debug recibido"})



from rest_framework_simplejwt.views import TokenObtainPairView
from lynx.serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
