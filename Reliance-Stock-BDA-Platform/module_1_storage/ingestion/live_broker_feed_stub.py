"""
live_broker_feed_stub.py — Live Broker WebSocket & Tick Stream Stub
====================================================================
Simulates high-velocity trading ticks (LTP, bid/ask, trade volume, timestamp)
for Reliance during Indian market hours (09:15 to 15:30 IST).
Structured for immediate integration with Angel One SmartAPI or Zerodha Kite Connect WebSocket.

Usage:
    python module_1_storage/ingestion/live_broker_feed_stub.py [--count 50] [--interval 0.5]
"""

import time
import json
import random
import argparse
import datetime
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def generate_mock_broker_tick(base_price: float = 2750.0) -> dict:
    """Generates an individual Indian stock market tick payload."""
    spread = round(random.uniform(0.05, 0.35), 2)
    noise = round(random.uniform(-1.50, 1.50), 2)
    ltp = round(base_price + noise, 2)
    bid = round(ltp - spread, 2)
    ask = round(ltp + spread, 2)
    volume = random.randint(10, 500)

    return {
        "ticker": "RELIANCE",
        "exchange": "NSE",
        "timestamp": datetime.datetime.now().isoformat(),
        "ltp": ltp,
        "bid": bid,
        "ask": ask,
        "volume": volume,
        "depth": {
            "buy_orders": random.randint(1000, 5000),
            "sell_orders": random.randint(1000, 5000)
        }
    }


def stream_mock_broker_ticks(count: int = 20, interval_sec: float = 0.5):
    """Streams simulated ticks to stdout or Kafka producer."""
    print("  [STREAM] Connecting to Broker WebSocket Stream for RELIANCE (NSE)...")
    price = 2750.0
    for i in range(count):
        tick = generate_mock_broker_tick(price)
        price = tick["ltp"]
        print(f"  [TICK #{i+1:03d}] LTP: Rs {tick['ltp']:.2f} | Bid: {tick['bid']:.2f} | Ask: {tick['ask']:.2f} | Vol: {tick['volume']}")
        time.sleep(interval_sec)
    print("  [OK] Mock tick streaming complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Broker WebSocket Streamer Stub")
    parser.add_argument("--count", type=int, default=10, help="Number of ticks to simulate")
    parser.add_argument("--interval", type=float, default=0.1, help="Interval between ticks in seconds")
    args = parser.parse_args()

    stream_mock_broker_ticks(args.count, args.interval)
