# ledger/models.py
import uuid
from django.db import models


class LedgerEntry(models.Model):
    ENTRY_TYPES = (
        ("DEBIT", "DEBIT"),
        ("CREDIT", "CREDIT"),
    )

    id = models.BigAutoField(primary_key=True)

    transaction_id = models.UUIDField()
    wallet_id = models.UUIDField()

    entry_type = models.CharField(max_length=16, choices=ENTRY_TYPES)
    amount = models.DecimalField(max_digits=18, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["transaction_id", "wallet_id", "entry_type"],
                name="unique_ledger_entry_per_side",
            )
        ]

class LedgerProcessedEvent(models.Model):
    transaction_id = models.UUIDField(primary_key=True)
    processed_at = models.DateTimeField(auto_now_add=True)

class OutboxEvent(models.Model):
    EVENT_TYPES = (
        ("LEDGER_SUCCESS", "LEDGER_SUCCESS"),
        ("LEDGER_FAILED", "LEDGER_FAILED"),
    )

    id = models.BigAutoField(primary_key=True)
    event_type = models.CharField(max_length=64, choices=EVENT_TYPES)
    payload = models.JSONField()

    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
