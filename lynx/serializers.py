from rest_framework import serializers
from .models import *

#=================================================================
# SERIALIZER USUARIO
#=================================================================
class UsuarioSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()  

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'saldo_virtual', 'reputacion', 'avatar_base64',
            'verificado', 'nombre_completo'  
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}"

#=================================================================
# SERIALIZER VIDEOJUEGO
#=================================================================
class VideojuegoSerializer(serializers.ModelSerializer):
    imagen_portada = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Videojuego
        fields = [
            'id', 'titulo', 'descripcion', 'genero', 'precio',
            'desarrollador', 'distribuidor',
            'requisitos_minimos', 'requisitos_recomendados',
            'soporte_mando', 'fecha_lanzamiento',
            'imagen_portada',  # campo de entrada desde el frontend
            'imagen_portada_base64',  # el campo real del modelo
            'disponible'
        ]
        read_only_fields = ['imagen_portada_base64']

    def create(self, validated_data):
        imagen = validated_data.pop('imagen_portada', None)

        print("🛰️ VIDEOJUEGO RECIBIDO DESDE EL FRONTEND:")
        for k, v in validated_data.items():
            print(f"  ├── {k}: {v}")
        if imagen:
            print("  └── ✅ Imagen base64 recibida (truncada):", imagen[:80], "...")

            validated_data['imagen_portada_base64'] = imagen
        else:
            print("  └── ⚠️ No se recibió imagen base64.")

        return super().create(validated_data)



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
        token['rol'] = user.rol
        token['user_id'] = user.id  
        return token


#=================================================================
# SERIALIZER USUARIO PERFIL (DETALLADO)
#=================================================================
class UsuarioPerfilSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'saldo_virtual', 'reputacion', 'avatar_base64',
            'verificado', 'nombre_completo'
        ]

    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}"



#================================================================

#=================================================================
# SERIALIZER ITEM
#=================================================================
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'nombre', 'descripcion', 'rareza', 'imagen_base64', 'juego']

#=================================================================
# SERIALIZER INVENTARIO ITEM
#=================================================================
class ItemSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'nombre', 'descripcion', 'rareza', 'imagen_base64']

class InventarioItemSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    item = ItemSerializerSimple(read_only=True)

    class Meta:
        model = InventarioItem
        fields = ['id', 'usuario', 'item', 'cantidad']

#=================================================================
# SERIALIZER ITEM EN VENTA
#=================================================================
class ItemEnVentaSerializer(serializers.ModelSerializer):
    vendedor = UsuarioSerializer(read_only=True)
    item = ItemSerializer(read_only=True)

    class Meta:
        model = ItemEnVenta
        fields = ['id', 'vendedor', 'item', 'precio', 'fecha']

#=================================================================
# SERIALIZER → LISTAR ÍTEMS EN VENTA EN EL MARKETPLACE
#=================================================================
class ItemMarketplaceSerializer(serializers.ModelSerializer):
    vendedor = UsuarioSerializer(read_only=True)
    item = ItemSerializer(read_only=True)

    class Meta:
        model = ItemEnVenta
        fields = ['id', 'vendedor', 'item', 'precio', 'fecha']

#=================================================================
# SERIALIZER → COMPRAR ÍTEM (SOLO SE NECESITA EL ID DEL ITEMENVENTA)
#=================================================================
class MarketplaceCompraSerializer(serializers.Serializer):
    item_en_venta_id = serializers.IntegerField()

    def validate_item_en_venta_id(self, value):
        from lynx.models import ItemEnVenta

        try:
            item_en_venta = ItemEnVenta.objects.get(id=value)
        except ItemEnVenta.DoesNotExist:
            raise serializers.ValidationError("El ítem en venta no existe.")

        return value

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


# SERIALIZER MENSAJE PRIVADO
class MensajePrivadoSerializer(serializers.ModelSerializer):
    emisor = UsuarioSerializer(read_only=True)
    receptor = UsuarioSerializer(read_only=True)

    class Meta:
        model = MensajePrivado
        fields = '__all__'

#=================================================================
# SERIALIZER REGISTRO VALIDADO
#=================================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            'username', 'password', 'confirm_password', 'first_name',
            'last_name', 'email', 'rol', 'avatar_base64'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Las contraseñas no coinciden."})
        return data

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre es obligatorio.")
        return value

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Los apellidos son obligatorios.")
        return value

    def validate_email(self, value):
        allowed_domains = ['@gmail.com', '@hotmail.com']
        if not any(domain in value for domain in allowed_domains):
            raise serializers.ValidationError("El email debe ser de dominio @gmail.com o @hotmail.com.")
        return value

    def validate_rol(self, value):
        valid_roles = [choice[0] for choice in Usuario.RolChoices.choices]
        if value not in valid_roles:
            raise serializers.ValidationError("El rol seleccionado no es válido.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        return Usuario.objects.create_user(**validated_data)
