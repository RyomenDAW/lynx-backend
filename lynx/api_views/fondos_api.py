# fondos_api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from decimal import Decimal
import requests

#=================================================================
# API PARA AÑADIR FONDOS VIA PAYPAL (CREATE ORDER, CONFIRM ORDER)
#=================================================================

class CrearOrdenFondosAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        monto = request.data.get('monto')
        if not monto or float(monto) <= 0:
            return Response({'error': 'Monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Aquí podrías registrar orden en base de datos si quieres control total

        return Response({'ok': True, 'mensaje': 'Orden preparada en frontend. Procede a PayPal.'})


class ConfirmarPagoPaypalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('orderID')
        if not order_id:
            return Response({'error': 'No orderID recibido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener access token PayPal
        auth_response = requests.post(
            'https://api-m.sandbox.paypal.com/v1/oauth2/token',
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
            data={'grant_type': 'client_credentials'}
        )
        if auth_response.status_code != 200:
            return Response({'error': 'Error obteniendo access token.'}, status=status.HTTP_400_BAD_REQUEST)

        access_token = auth_response.json().get('access_token')

        # Consultar la orden en PayPal
        order_response = requests.get(
            f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        order_data = order_response.json()

        if order_response.status_code == 200 and order_data.get('status') == 'COMPLETED':
            amount = Decimal(order_data['purchase_units'][0]['amount']['value'])

            # Añadir saldo
            request.user.saldo_virtual += amount
            request.user.save()

            return Response({'ok': True, 'nuevo_saldo': str(request.user.saldo_virtual)})
        else:
            return Response({'error': 'Orden no completada o inválida.'}, status=status.HTTP_400_BAD_REQUEST)
