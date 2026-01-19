# wallets/services.py
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Wallet, WalletReservation, OutboxEvent


@transaction.atomic
def reserve_funds(*, wallet_id, transaction_id, amount, target_wallet_id):
    # Idempotency check
    if WalletReservation.objects.filter(
        transaction_id=transaction_id
    ).exists():
        print("Reservation already exists for transaction", transaction_id)
        return  # idempotent success

    wallet = (
        Wallet.objects
        .select_for_update()
        .get(id=wallet_id)
    )

    print("Wallet before reservation:", wallet)
    if wallet.available_balance < amount:
        raise ValidationError("Insufficient balance")

    wallet.available_balance -= amount
    wallet.reserved_balance += amount
    wallet.save()
    print("Wallet after reservation:", wallet)
    WalletReservation.objects.create(
        transaction_id=transaction_id,
        wallet_id=wallet_id,
        target_wallet_id=target_wallet_id,
        amount=amount,
    )

    print("Creating outbox event for transaction", transaction_id)
    OutboxEvent.objects.create(
        event_type="WALLET_RESERVED",
        payload={
            "transaction_id": str(transaction_id),
            "wallet_id": str(wallet_id),
            "amount": str(amount),
        },
    )


# wallets/services.py
from django.db import transaction

from wallets.models import (
    Wallet,
    WalletReservation,
    WalletFinalization,
)


@transaction.atomic
def finalize_success(*, transaction_id):
    if WalletFinalization.objects.filter(
        transaction_id=transaction_id
    ).exists():
        return

    reservation = WalletReservation.objects.select_for_update().get(
        transaction_id=transaction_id
    )

    sender_wallet = Wallet.objects.select_for_update().get(
        id=reservation.wallet_id
    )

    receiver_wallet = Wallet.objects.select_for_update().get(
        id=reservation.target_wallet_id
    )

    # Apply final state
    sender_wallet.reserved_balance -= reservation.amount
    sender_wallet.save()

    receiver_wallet.available_balance += reservation.amount
    receiver_wallet.save()

    WalletFinalization.objects.create(
        transaction_id=transaction_id,
        status="SUCCESS",
    )


@transaction.atomic
def finalize_failure(*, transaction_id):
    if WalletFinalization.objects.filter(
        transaction_id=transaction_id
    ).exists():
        return

    reservation = WalletReservation.objects.select_for_update().get(
        transaction_id=transaction_id
    )

    sender_wallet = Wallet.objects.select_for_update().get(
        id=reservation.wallet_id
    )

    sender_wallet.reserved_balance -= reservation.amount
    sender_wallet.available_balance += reservation.amount
    sender_wallet.save()

    WalletFinalization.objects.create(
        transaction_id=transaction_id,
        status="FAILED",
    )
