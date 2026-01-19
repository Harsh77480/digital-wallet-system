# transactions/serializers.py
from rest_framework import serializers
from .models import Transaction


class TransferSerializer(serializers.Serializer):
    sender_wallet_id = serializers.UUIDField()
    receiver_wallet_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    idempotency_key = serializers.CharField(max_length=128)

    def create(self, validated_data):
        tx, _ = Transaction.objects.get_or_create(
            idempotency_key=validated_data["idempotency_key"],
            defaults={
                "sender_wallet_id": validated_data["sender_wallet_id"],
                "receiver_wallet_id": validated_data["receiver_wallet_id"],
                "amount": validated_data["amount"],
            },
        )
        return tx
