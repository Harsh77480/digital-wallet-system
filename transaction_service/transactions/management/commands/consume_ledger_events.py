# transactions/management/commands/consume_ledger_events.py
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from confluent_kafka import Consumer

from transactions.models import Transaction, TransactionStatus


class Command(BaseCommand):
    help = "Consume ledger events and update transaction state"

    def handle(self, *args, **options):
        consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "transaction-service",
                "auto.offset.reset": "earliest",
                "enable.auto.commit": False,
            }
        )

        consumer.subscribe([settings.LEDGER_EVENTS_TOPIC])

        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            if msg.error():
                raise RuntimeError(msg.error())

            self.process_message(msg)
            consumer.commit(msg)

    
    def process_message(self, msg):
        data = json.loads(msg.value().decode())

        event_type = data["event_type"]
        transaction_id = data["transaction_id"]

        with transaction.atomic():
            tx = Transaction.objects.select_for_update().get(
                id=transaction_id
            )

            # Terminal states are immutable
            if tx.status in (
                TransactionStatus.SUCCESS,
                TransactionStatus.FAILED,
            ):
                return

            if event_type == "LEDGER_SUCCESS":
                tx.status = TransactionStatus.SUCCESS
                tx.save()

            elif event_type == "LEDGER_FAILED":
                tx.status = TransactionStatus.FAILED
                tx.save()

    