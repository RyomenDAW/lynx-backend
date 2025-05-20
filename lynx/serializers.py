from rest_framework import serializers
from .models import Usuario, Videojuego, Biblioteca, Reseña, Item, TransaccionItem, CodigoPromocional, Amistad

#=================================================================
# SERIALIZER USUARIO
#=================================================================
class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()  # 👈 AÑADIDO

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'saldo_virtual', 'reputacion', 'avatar_base64',
            'verificado', 'nombre_completo'  # 👈 INCLUIDO
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}"

#=================================================================
# SERIALIZER VIDEOJUEGO
#=================================================================
class VideojuegoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videojuego
        fields = '__all__'


#=================================================================
# SERIALIZER BIBLIOTECA
#=================================================================
class BibliotecaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    juego = VideojuegoSerializer(read_only=True)

    class Meta:
        model = Biblioteca
        fields = '__all__'


#=================================================================
# SERIALIZER RESEÑA
#=================================================================
class ReseñaSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    juego = VideojuegoSerializer(read_only=True)

    class Meta:
        model = Reseña
        fields = '__all__'


#=================================================================
# SERIALIZER ITEM
#=================================================================
class ItemSerializer(serializers.ModelSerializer):
    juego = VideojuegoSerializer(read_only=True)

    class Meta:
        model = Item
        fields = '__all__'


#=================================================================
# SERIALIZER TRANSACCION ITEM
#=================================================================
class TransaccionItemSerializer(serializers.ModelSerializer):
    vendedor = UsuarioSerializer(read_only=True)
    comprador = UsuarioSerializer(read_only=True)
    item = ItemSerializer(read_only=True)

    class Meta:
        model = TransaccionItem
        fields = '__all__'


#=================================================================
# SERIALIZER CODIGO PROMOCIONAL
#=================================================================
class CodigoPromocionalSerializer(serializers.ModelSerializer):
    # Mantén el serializer para lectura:
    videojuego = VideojuegoSerializer(read_only=True)
    videojuego_id = serializers.PrimaryKeyRelatedField(
        queryset=Videojuego.objects.all(),
        source='videojuego',
        write_only=True,
        required=False,
        allow_null=True,
    )
    usuario_ultimo = UsuarioSerializer(read_only=True)

    class Meta:
        model = CodigoPromocional
        fields = [
            'id', 'codigo_texto', 'descripcion', 'videojuego', 'videojuego_id', 
            'saldo_extra', 'usos_totales', 'usos_actuales', 'usado', 
            'fecha_expiracion', 'usuario_ultimo'
        ]


#=================================================================
# SERIALIZER AMISTAD
#=================================================================
class AmistadSerializer(serializers.ModelSerializer):
    solicitante = UsuarioSerializer(read_only=True)
    receptor = UsuarioSerializer(read_only=True)

    class Meta:
        model = Amistad
        fields = '__all__'





from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['rol'] = user.rol  # ACCESO DIRECTO, ES CHARFIELD
        return token
