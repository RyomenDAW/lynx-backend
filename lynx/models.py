
from django.db import models
import base64

from django.contrib.auth.models import AbstractUser

#=================================================================
# MODELO PERSONALIZADO DE USUARIO BASADO EN AbstractUser
#=================================================================
class Usuario(AbstractUser):
    # A PARTIR DE AQUÍ PUEDES DEFINIR TUS CAMPOS EXTRA

    class RolChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        MOD = 'MOD', 'Moderador'
        DIST = 'DIST', 'Distribuidor Oficial'
        SOP = 'SOP', 'Soporte Técnico'
        USER = 'USER', 'Usuario Estándar'
        COL = 'COL', 'Colaborador'
        TRADER = 'TRADER', 'Trader'

    # YA TIENES: username, first_name, last_name, email, password, is_staff, is_superuser, etc.

    rol = models.CharField(
        max_length=10,
        choices=RolChoices.choices,
        default=RolChoices.USER
    )
    
    saldo_virtual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reputacion = models.IntegerField(default=0)
    avatar_base64 = models.TextField(blank=True, null=True)
    verificado = models.BooleanField(default=False)

    def set_avatar_from_file(self, file):
        self.avatar_base64 = "data:image/jpeg;base64," + base64.b64encode(file.read()).decode()

    def __str__(self):
        return self.username


#=================================================================
# MODELO DE VIDEOJUEGOS DISPONIBLES EN LA TIENDA
#=================================================================
class Videojuego(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    genero = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    desarrollador = models.CharField(max_length=100)
    distribuidor = models.CharField(max_length=100)
    requisitos_minimos = models.TextField()
    requisitos_recomendados = models.TextField()
    soporte_mando = models.BooleanField(default=False)
    fecha_lanzamiento = models.DateField()

    # IMAGEN EN FORMATO BASE64
    imagen_portada_base64 = models.TextField(blank=True, null=True)

    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    # MÉTODO PARA GUARDAR IMAGEN EN BASE64
    def set_imagen_portada_from_file(self, file):
        self.imagen_portada_base64 = "data:image/jpeg;base64," + base64.b64encode(file.read()).decode()

#=================================================================
# BIBLIOTECA DEL USUARIO → RELACIÓN N:M ENTRE USUARIO Y VIDEOJUEGO
#=================================================================
class Biblioteca(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    juego = models.ForeignKey(Videojuego, on_delete=models.CASCADE)

    fecha_adquisicion = models.DateField(auto_now_add=True)
    favorito = models.BooleanField(default=False)
    tiempo_jugado = models.PositiveIntegerField(default=0)  # EN MINUTOS

    # ESTA RELACIÓN PERMITE SABER QUÉ JUEGOS POSEE UN USUARIO

    def __str__(self):
        return f"{self.usuario} - {self.juego}"

#=================================================================
# RESEÑAS QUE UN USUARIO ESCRIBE SOBRE UN VIDEOJUEGO
#=================================================================
class Reseña(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    juego = models.ForeignKey(Videojuego, on_delete=models.CASCADE)

    puntuacion = models.IntegerField()  # 0 A 10
    comentario = models.TextField(max_length=1000, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    votos_positivos = models.PositiveIntegerField(default=0)
    votos_negativos = models.PositiveIntegerField(default=0)

    # UN JUEGO PUEDE TENER MUCHAS RESEÑAS, UN USUARIO PUEDE ESCRIBIR MUCHAS

    def __str__(self):
        return f"{self.usuario} → {self.juego}"

#=================================================================
# ÍTEMS VIRTUALES RELACIONADOS O NO CON UN VIDEOJUEGO
#=================================================================
class Item(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    rareza = models.CharField(max_length=50)

    # IMAGEN EN FORMATO BASE64
    imagen_base64 = models.TextField(blank=True, null=True)

    # RELACIÓN OPCIONAL CON UN VIDEOJUEGO (COSMÉTICOS, SKINS, ETC.)
    juego = models.ForeignKey(Videojuego, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

    # MÉTODO PARA GUARDAR LA IMAGEN
    def set_imagen_from_file(self, file):
        self.imagen_base64 = "data:image/jpeg;base64," + base64.b64encode(file.read()).decode()

#=================================================================
# TRANSACCIONES ENTRE USUARIOS CON ÍTEMS
#=================================================================
class TransaccionItem(models.Model):
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ventas')
    comprador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='compras')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
    tipo_transaccion = models.CharField(max_length=50)  # EJEMPLO: 'VENTA', 'INTERCAMBIO'

    # UN ITEM PUEDE HABERSE VENDIDO VARIAS VECES
    # UN USUARIO PUEDE COMPRAR Y VENDER MUCHOS ITEMS

    def __str__(self):
        return f"{self.vendedor} → {self.comprador} ({self.item})"

#=================================================================
# CÓDIGOS PROMOCIONALES CANJEABLES POR ÍTEMS
#=================================================================
class CodigoPromocional(models.Model):
    codigo_texto = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    fecha_expiracion = models.DateField()
    usado = models.BooleanField(default=False)

    # RELACIÓN: UN CÓDIGO VA LIGADO A UN ITEM ESPECÍFICO

    def __str__(self):
        return self.codigo_texto
