from rest_framework import serializers
from .models import Usuario, Videojuego, Biblioteca, Reseña, Item, TransaccionItem, CodigoPromocional, Amistad

#=================================================================
# SERIALIZER USUARIO
#=================================================================
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 'saldo_virtual', 'reputacion', 'avatar_base64', 'verificado']


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
    videojuego = VideojuegoSerializer(read_only=True)
    usuario_ultimo = UsuarioSerializer(read_only=True)

    class Meta:
        model = CodigoPromocional
        fields = '__all__'


#=================================================================
# SERIALIZER AMISTAD
#=================================================================
class AmistadSerializer(serializers.ModelSerializer):
    solicitante = UsuarioSerializer(read_only=True)
    receptor = UsuarioSerializer(read_only=True)

    class Meta:
        model = Amistad
        fields = '__all__'
