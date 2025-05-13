from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Opcional: puedes dejarlo o quitarlo si no quieres usar admin de Django
    path('api/', include('lynx.api_urls')),  # ✅ Solo el API expuesto a Angular
]
