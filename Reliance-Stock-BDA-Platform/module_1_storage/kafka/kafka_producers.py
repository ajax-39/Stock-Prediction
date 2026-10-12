"""
kafka_producers.py — Speed Layer Producer for Ticks & Breaking News
===================================================================
Streams simulated high-velocity broker ticks to Kafka topic 'reliance-ticks'
and breaking news headlines to 'reliance-news'.

Usage:
    python module_1_storage/kafka/kafka_producers.py [--topic reliance-ticks] [--count 30] [--bootstrap localhost:29092]
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import json
import random
import argparse
import datetime

DEFAULT_BOOTSTRAP = "localhost:29092"


def get_kafka_producer(bootstrap_servers: str):
    """Initializes KafkaProducer with JSON serialization."""
    try:
        from kafka import KafkaProducer
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers.split(","),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            request_timeout_ms=3000
        )
        return producer
    except Exception as e:
        print(f"  [INFO] Kafka broker at {bootstrap_servers} not accessible ({e}). Running in simulated stream mode.")
        return None


def stream_ticks(producer, topic: str = "reliance-ticks", count: int = 15, interval: float = 0.1):
    """Produces live trading ticks to Kafka topic."""
    print(f"  [KAFKA] Streaming {count} ticks to topic '{topic}'...")
    price = 2748.50
    for i in range(count):
        price += round(random.uniform(-1.20, 1.40), 2)
        payload = {
            "ticker": "RELIANCE",
            "timestamp": datetime.datetime.now().isoformat(),
            "ltp": round(price, 2),
            "bid": round(price - 0.20, 2),
            "ask": round(price + 0.20, 2),
            "volume": random.randint(50, 800)
        }
        if producer:
            try:
                producer.send(topic, payload)
            except Exception:
                pass
        print(f"    [Kafka Tick #{i+1:02d}] LTP: Rs {payload['ltp']} | Vol: {payload['volume']}")
        time.sleep(interval)

    if producer:
        producer.flush()
    print("  [OK] Tick streaming session finished.")


def stream_news(producer, topic: str = "reliance-news"):
    """Produces news payload to Kafka."""
    news_event = {
        "ticker": "RELIANCE",
        "trade_date": datetime.date.today().isoformat(),
        "title": "Jio Financial Services Expands Retail Merchant Lending Ecosystem",
        "summary": "Digital lending originations hit new record with accelerated penetration across Tier 2 and Tier 3 cities.",
        "polarity_score": 0.42,
        "sentiment_label": "POSITIVE",
        "published_at": datetime.datetime.now().isoformat()
    }
    if producer:
        try:
            producer.send(topic, news_event)
            producer.flush()
        except Exception:
            pass
    print(f"  [KAFKA-NEWS] Published news event to '{topic}': {news_event['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kafka Producer for Reliance Speed Layer")
    parser.add_argument("--bootstrap", default=DEFAULT_BOOTSTRAP, help="Kafka bootstrap server")
    parser.add_argument("--count", type=int, default=10, help="Number of ticks to emit")
    parser.add_argument("--topic", default="reliance-ticks", help="Target topic")
    args = parser.parse_args()

    producer = get_kafka_producer(args.bootstrap)
    stream_ticks(producer, topic=args.topic, count=args.count)
    stream_news(producer)
