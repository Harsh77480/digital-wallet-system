# transactions/models.py
import uuid
from django.db import models


class TransactionStatus(models.TextChoices):
    INITIATED = "INITIATED"
    PENDING_LEDGER = "PENDING_LEDGER"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender_wallet_id = models.UUIDField()
    receiver_wallet_id = models.UUIDField()

    amount = models.DecimalField(max_digits=18, decimal_places=2)

    idempotency_key = models.CharField(max_length=128)

    status = models.CharField(
        max_length=32,
        choices=TransactionStatus.choices,
        default=TransactionStatus.INITIATED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["idempotency_key"],
                name="unique_transaction_idempotency",
            )
        ]
