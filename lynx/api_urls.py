# api_urls.py

from django.urls import path
from rest_framework.routers import DefaultRouter

# IMPORTA TUS VIEWSETS
from lynx.api_views.usuarios_api import UsuarioViewSet, RegisterView, CustomTokenObtainPairView, UsuarioPerfilView
from lynx.api_views.videojuegos_api import VideojuegoViewSet
from lynx.api_views.biblioteca_api import BibliotecaViewSet
from lynx.api_views.codigos_api import CodigoPromocionalViewSet
from lynx.api_views.items_api import ItemViewSet
from lynx.api_views.reseñas_api import ReseñaViewSet
from lynx.api_views.social_api import SocialViewSet
from lynx.api_views.transacciones_api import TransaccionItemViewSet
from lynx.api_views.fondos_api import CrearOrdenFondosAPIView, ConfirmarPagoPaypalAPIView

# 🔹 AÑADE ESTO BIEN:
from lynx.api_views.steam_api import BuscarSteamAPIView, DetallesSteamAPIView

from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'videojuegos', VideojuegoViewSet, basename='videojuego')
router.register(r'biblioteca', BibliotecaViewSet, basename='biblioteca')
router.register(r'codigos', CodigoPromocionalViewSet, basename='codigo')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'reseñas', ReseñaViewSet, basename='reseña')
router.register(r'social', SocialViewSet, basename='social')
router.register(r'transacciones', TransaccionItemViewSet, basename='transaccion')

urlpatterns = router.urls + [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('fondos/crear/', CrearOrdenFondosAPIView.as_view(), name='crear_orden_fondos'),
    path('fondos/confirmar/', ConfirmarPagoPaypalAPIView.as_view(), name='confirmar_pago_paypal'),

    # ✅ AÑADE ESTAS DOS
    path('steam-search/', BuscarSteamAPIView.as_view(), name='steam-search'),
    path('steam-details/', DetallesSteamAPIView.as_view(), name='steam-details'),  # <-- ESTA TE FALTA
]
