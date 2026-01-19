# wallets/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ReserveSerializer
from  .services  import reserve_funds


class HealthView(APIView):
    def get(self, request):
        return Response({"ok": True})

class ReserveFundsView(APIView):
    def post(self, request):
        serializer = ReserveSerializer(data=request.data)

        if not serializer.is_valid():
            print(serializer.errors)   # IMPORTANT
            return Response(serializer.errors, status=400)
        
        print("ReserveFundsView - valid data:", serializer.validated_data)  # IMPORTANT
        reserve_funds(**serializer.validated_data)

        return Response(status=status.HTTP_200_OK)

