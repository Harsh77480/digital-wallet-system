# wallets/models.py
import uuid
from django.db import models


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    available_balance = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )
    reserved_balance = models.DecimalField(
        max_digits=18, decimal_places=2, default=0
    )

    created_at = models.DateTimeField(auto_now_add=True)



class WalletReservation(models.Model):
    transaction_id = models.UUIDField(primary_key=True)
    wallet_id = models.UUIDField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    target_wallet_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

class OutboxEvent(models.Model):
    EVENT_TYPES = (
        ("WALLET_RESERVED", "WALLET_RESERVED"),
    )

    id = models.BigAutoField(primary_key=True)
    event_type = models.CharField(max_length=64, choices=EVENT_TYPES)

    payload = models.JSONField()

    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



class WalletFinalization(models.Model):
    transaction_id = models.UUIDField(primary_key=True)
    status = models.CharField(
        max_length=32,
        choices=(
            ("SUCCESS", "SUCCESS"),
            ("FAILED", "FAILED"),
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
