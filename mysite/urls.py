from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('lynx.api_urls')),  # 👈 ASEGÚRATE QUE ESTA LÍNEA EXISTE
]
