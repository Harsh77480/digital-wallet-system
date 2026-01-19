# wallets/management/commands/consume_ledger_events.py
import json

from django.conf import settings
from django.core.management.base import BaseCommand

from confluent_kafka import Consumer

from wallets.services import (
    finalize_success,
    finalize_failure,
)


class Command(BaseCommand):
    help = "Consume ledger outcome events and finalize wallets"

    def handle(self, *args, **options):
        consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "wallet-service",
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

        if event_type == "LEDGER_SUCCESS":
            finalize_success(transaction_id=transaction_id)

        elif event_type == "LEDGER_FAILED":
            finalize_failure(transaction_id=transaction_id)
