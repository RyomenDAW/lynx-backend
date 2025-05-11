from django.contrib import admin
from django.urls import path
from lynx.views import *
from . import views

urlpatterns = [
    path('', inicio, name='inicio'),
    path('registro/', registro_view, name='registro'),
    path('videojuegos/', views.lista_videojuegos, name='lista_videojuegos'),
    path('videojuegos/crear/', views.crear_videojuego, name='crear_videojuego'),
    path('videojuegos/editar/<int:id>/', views.editar_videojuego, name='editar_videojuego'),
    path('videojuegos/eliminar/<int:id>/', views.eliminar_videojuego, name='eliminar_videojuego'),
    path('videojuegos/importar/', views.importar_desde_steam, name='importar_desde_steam'),
    path('videojuegos/<int:id>/', views.detalle_videojuego, name='detalle_videojuego'),
    path('videojuegos/buscar-steam/', views.buscar_juegos_steam, name='buscar_juegos_steam'),
    path('videojuegos/importar-steam/<int:appid>/', views.importar_desde_steam_por_appid, name='importar_desde_steam_por_appid'),


    path('biblioteca/', views.biblioteca_usuario, name='biblioteca'),
    path('comprar/<int:id>/', views.comprar_videojuego, name='comprar_videojuego'),
    path('marcar_favorito/<int:biblioteca_id>/', views.marcar_favorito, name='marcar_favorito'),
    path('eliminar_de_biblioteca/<int:biblioteca_id>/', views.eliminar_de_biblioteca, name='eliminar_de_biblioteca'),
    path('biblioteca/tiempo/<int:biblioteca_id>/', views.añadir_tiempo_jugado, name='añadir_tiempo'),

    path('reseña/crear/<int:juego_id>/', views.crear_reseña, name='crear_reseña'),
    path('reseñas/videojuego/<int:juego_id>/', views.ver_reseñas, name='ver_reseñas'),
    path('reseña/editar/<int:id>/', views.editar_reseña, name='editar_reseña'),
    path('reseña/eliminar/<int:id>/', views.eliminar_reseña, name='eliminar_reseña'),

    # Solo para usuarios
    path('codigos/canjear/', views.canjear_codigo, name='canjear_codigo'),

    # Solo para admin/mod
    path('codigos/', views.lista_codigos, name='lista_codigos'),
    path('codigos/crear/', views.crear_codigo, name='crear_codigo'),
    path('codigos/editar/<int:id>/', views.editar_codigo, name='editar_codigo'),
    path('codigos/eliminar/<int:id>/', views.eliminar_codigo, name='eliminar_codigo'),


    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('usuarios/', ver_usuarios, name='ver_usuarios'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # --- VISTAS SOCIALES ---
    path('social/amigos/', views.ver_amigos, name='ver_amigos'),
    path('social/enviar/<int:id>/', views.enviar_solicitud, name='enviar_solicitud'),
    path('social/aceptar/<int:id>/', views.aceptar_solicitud, name='aceptar_amistad'),
    path('social/rechazar/<int:id>/', views.rechazar_solicitud, name='rechazar_amistad'),
    path('social/eliminar/<int:id>/', views.eliminar_amigo, name='eliminar_amigo'),





]
