# wallets/serializers.py
from rest_framework import serializers



# wallets/serializers.py
class ReserveSerializer(serializers.Serializer):
    wallet_id = serializers.UUIDField()
    target_wallet_id = serializers.UUIDField()
    transaction_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)