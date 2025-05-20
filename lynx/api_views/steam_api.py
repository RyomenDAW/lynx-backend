# lynx/api_views/steam_api.py

import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

class BuscarSteamAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        termino = request.query_params.get('q')
        if not termino:
            return Response({"error": "Parámetro de búsqueda requerido."}, status=400)
        url = f"https://store.steampowered.com/api/storesearch?term={termino}&cc=es&l=spanish"
        steam = requests.get(url)
        return Response(steam.json())


class DetallesSteamAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        appid = request.query_params.get('appid')
        if not appid:
            return Response({"error": "AppID requerido."}, status=400)
        url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=es&l=spanish"
        steam = requests.get(url)
        return Response(steam.json())
