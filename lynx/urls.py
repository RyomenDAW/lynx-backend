from django.contrib import admin
from django.urls import path
from lynx.views import *

urlpatterns = [
    path('', inicio, name='inicio'),
    path('registro/', registro_view, name='registro'),

]
