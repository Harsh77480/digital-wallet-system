# ledger/management/commands/publish_outbox.py
import json
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from confluent_kafka import Producer

from ledger.models import OutboxEvent


class Command(BaseCommand):
    help = "Publish ledger outbox events to Kafka"

    def handle(self, *args, **options):
        producer = Producer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "acks": "all",
                "linger.ms": 5,
            }
        )

        while True:
            events = (
                OutboxEvent.objects
                .filter(published=False)
                .order_by("id")[:50]
            )

            if not events:
                time.sleep(1)
                continue

            for event in events:
                self.publish_event(producer, event)

            producer.flush()

    def publish_event(self, producer, event: OutboxEvent):
        payload = json.dumps(
            {
                "event_type": event.event_type,
                **event.payload,
            }
        )

        def delivery_report(err, msg):
            if err:
                raise RuntimeError(f"Kafka delivery failed: {err}")

            OutboxEvent.objects.filter(id=event.id).update(published=True)

        producer.produce(
            topic=settings.LEDGER_EVENTS_TOPIC,
            key=event.payload["transaction_id"],
            value=payload,
            on_delivery=delivery_report,
        )
