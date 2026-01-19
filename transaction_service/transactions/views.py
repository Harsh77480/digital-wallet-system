# transactions/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TransferSerializer
from transactions.services import initiate_transfer


class TransferView(APIView):
    def post(self, request):

        serializer = TransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        initiate_transfer(transaction)

        return Response(
            {
                "transaction_id": str(transaction.id),
                "status": transaction.status,
            },
            status=status.HTTP_200_OK,
        )
