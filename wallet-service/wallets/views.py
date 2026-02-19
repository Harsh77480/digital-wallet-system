# wallets/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ReserveSerializer
from  .services  import reserve_funds
from django.db import transaction

class HealthView(APIView):
    def get(self, request):
        return Response({"ok": True})

class ReserveFundsView(APIView): # called synchronously from transaction service when a transfer is initiated. 
    def post(self, request):
        try : 
            serializer = ReserveSerializer(data=request.data)
            serializer.is_valid(raise_exception=True) 
            print("ReserveFundsView - valid data:", serializer.validated_data)  # IMPORTANT
            reserve_funds(**serializer.validated_data) # if reserve_funds raises an exception, the transaction will be rolled back and also it will trigger the except block. 
            return Response(status=status.HTTP_200_OK)
        except Exception as e : 
            return Response(serializer.errors, status=400)

