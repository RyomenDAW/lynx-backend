from django.urls import path, include

urlpatterns = [
    path('api/', include('lynx.api_urls')),
]
