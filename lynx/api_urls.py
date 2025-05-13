# api_urls.py

from rest_framework.routers import DefaultRouter
from lynx.api_views.usuarios_api import UsuarioViewSet
from lynx.api_views.videojuegos_api import VideojuegoViewSet
from lynx.api_views.biblioteca_api import BibliotecaViewSet
from lynx.api_views.codigos_api import CodigoPromocionalViewSet
from lynx.api_views.items_api import ItemViewSet
from lynx.api_views.reseñas_api import ReseñaViewSet
from lynx.api_views.social_api import SocialViewSet
from lynx.api_views.transacciones_api import TransaccionItemViewSet
from lynx.api_views.fondos_api import CrearOrdenFondosAPIView, ConfirmarPagoPaypalAPIView
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
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
    path('fondos/crear/', CrearOrdenFondosAPIView.as_view(), name='crear_orden_fondos'),
    path('fondos/confirmar/', ConfirmarPagoPaypalAPIView.as_view(), name='confirmar_pago_paypal'),


    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token
]
