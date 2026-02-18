# transaction_service/transactions/services.py
import requests
from django.conf import settings
from transactions.models import TransactionStatus


def initiate_transfer(tx): # calling wallet service synchronously to check balance and reserve money, this is an optimization to fail fast.
    r = requests.post(
        f"{settings.WALLET_SERVICE_BASE_URL}/reserve",
        json={
            "wallet_id": str(tx.sender_wallet_id), 
            "target_wallet_id": str(tx.receiver_wallet_id),
            "transaction_id": str(tx.id),
            "amount": str(tx.amount),
        },
        timeout=3,
    )

    if r.status_code != 200:
        tx.status = TransactionStatus.FAILED
        tx.save(update_fields=["status"])
        raise Exception("Wallet reserve failed")

    tx.status = TransactionStatus.PENDING_LEDGER
    tx.save(update_fields=["status"])
