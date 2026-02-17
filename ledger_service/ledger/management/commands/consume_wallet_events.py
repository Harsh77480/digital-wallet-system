# ledger/management/commands/consume_wallet_events.py
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction, IntegrityError

from confluent_kafka import Consumer

from ledger.models import (
    LedgerEntry,
    LedgerProcessedEvent,
    OutboxEvent,
)


class Command(BaseCommand):
    help = "Consume WALLET_RESERVED events and write ledger entries"

    def handle(self, *args, **options):
        consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "ledger-service",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )

        consumer.subscribe([settings.WALLET_EVENTS_TOPIC]) # wallet.events 

        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            if msg.error():
                raise RuntimeError(msg.error())

            self.process_message(msg)
            consumer.commit(msg)
            
    @transaction.atomic 
    def process_message(self, msg):
        data = json.loads(msg.value().decode())

        transaction_id = data["transaction_id"]
        sender_wallet_id = data["wallet_id"]
        amount = data["amount"]

        # NOTE:
        # We assume receiver_wallet_id is derivable later,
        # or included in event in next iteration.
        # For now, we focus on correctness of pattern.

        try:
            with transaction.atomic():
                print("Processing WALLET_RESERVED for transaction", transaction_id)

                if LedgerProcessedEvent.objects.filter(
                    transaction_id=transaction_id
                ).exists():
                    return
                
                print("No prior ledger processing found for transaction", transaction_id)

                # DEBIT sender
                LedgerEntry.objects.create(
                    transaction_id=transaction_id,
                    wallet_id=sender_wallet_id,
                    entry_type="DEBIT",
                    amount=amount,
                )

                print("Created DEBIT ledger entry for transaction", transaction_id)

                # CREDIT receiver (placeholder)
                LedgerEntry.objects.create(
                    transaction_id=transaction_id,
                    wallet_id=sender_wallet_id,
                    entry_type="CREDIT",
                    amount=amount,
                )
                
                print("Created CREDIT ledger entry for transaction", transaction_id)

                LedgerProcessedEvent.objects.create(
                    transaction_id=transaction_id
                )
                print("Marked transaction", transaction_id, "as processed in ledger")

                OutboxEvent.objects.create(
                    event_type="LEDGER_SUCCESS",
                    payload={
                        "transaction_id": transaction_id
                    },
                )

        except IntegrityError:
            # Idempotent duplicate
            return

        except Exception as e:
            print("Error processing WALLET_RESERVED event:", e)

            OutboxEvent.objects.create(
                event_type="LEDGER_FAILED",
                payload={
                    "transaction_id": transaction_id
                },
            )
