"""
hbase_loader.py — Load Real-Time Ticks, Scores & Predictions into HBase
========================================================================
Implements O(1) time-series lookups in Apache HBase using the reverse-timestamp
row-key pattern:
    RowKey = RELIANCE#<9999999999999 - epoch_millis>

Column Families:
    cf_tick: ltp, volume, bid, ask, timestamp
    cf_score: T, F, N, R, composite
    cf_pred: predicted_close, direction, signal, mae_range

Includes local JSON key-value persistence for seamless offline / standalone dashboard lookups.

Usage:
    python module_1_storage/hbase/hbase_loader.py [--host hbase-master] [--port 9090]
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import json
import time
import argparse
import datetime

TABLE_NAME = "reliance_serving"
MAX_TIMESTAMP = 9999999999999

LOCAL_FALLBACK_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "serving", "hbase_mock.json")
)


def generate_reverse_timestamp_rowkey(ticker: str = "RELIANCE", ts_millis: int = None) -> str:
    """Creates reverse timestamp row-key for instant latest-record scan."""
    if ts_millis is None:
        ts_millis = int(time.time() * 1000)
    rev_ts = str(MAX_TIMESTAMP - ts_millis).zfill(13)
    return f"{ticker}#{rev_ts}"


def put_serving_record(tick_data: dict = None, score_data: dict = None, pred_data: dict = None,
                       host: str = "hbase-master", port: int = 9090):
    """Inserts a multi-column family record into HBase or local fallback."""
    rowkey = generate_reverse_timestamp_rowkey()
    record = {
        "rowkey": rowkey,
        "ticker": "RELIANCE",
        "created_at": datetime.datetime.now().isoformat(),
        "cf_tick": tick_data or {
            "ltp": "2745.50", "volume": "3200", "bid": "2745.20", "ask": "2745.80",
            "timestamp": datetime.datetime.now().isoformat()
        },
        "cf_score": score_data or {
            "T": "74.5", "F": "68.0", "N": "78.2", "R": "65.0", "composite": "72.4"
        },
        "cf_pred": pred_data or {
            "predicted_close": "2768.40", "direction": "UP", "signal": "BUY", "mae_range": "24.50"
        }
    }

    inserted_to_hbase = False
    try:
        import happybase
        connection = happybase.Connection(host=host, port=port, timeout=3000)
        table = connection.table(TABLE_NAME)

        mutations = {}
        for col, val in record["cf_tick"].items():
            mutations[f"cf_tick:{col}".encode()] = str(val).encode()
        for col, val in record["cf_score"].items():
            mutations[f"cf_score:{col}".encode()] = str(val).encode()
        for col, val in record["cf_pred"].items():
            mutations[f"cf_pred:{col}".encode()] = str(val).encode()

        table.put(rowkey.encode(), mutations)
        connection.close()
        inserted_to_hbase = True
        print(f"  [HBase] Successfully stored rowkey {rowkey} in '{TABLE_NAME}'")
    except Exception:
        pass

    # Save to local fallback store for instant UI consumption
    os.makedirs(os.path.dirname(LOCAL_FALLBACK_FILE), exist_ok=True)
    existing = []
    if os.path.exists(LOCAL_FALLBACK_FILE):
        try:
            with open(LOCAL_FALLBACK_FILE, "r") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    existing.insert(0, record)
    existing = existing[:100]

    with open(LOCAL_FALLBACK_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    status_tag = "[HBase & Local Mirror]" if inserted_to_hbase else "[Local Mirror File]"
    print(f"  [STORAGE] {status_tag} Latest serving state saved. RowKey: {rowkey}")
    return record


def get_latest_serving_record(host: str = "hbase-master", port: int = 9090) -> dict:
    """Reads latest record from HBase (or local fallback)."""
    try:
        import happybase
        connection = happybase.Connection(host=host, port=port, timeout=3000)
        table = connection.table(TABLE_NAME)
        for key, data in table.scan(row_prefix=b"RELIANCE#", limit=1):
            connection.close()
            decoded = {k.decode(): v.decode() for k, v in data.items()}
            return decoded
    except Exception:
        pass

    if os.path.exists(LOCAL_FALLBACK_FILE):
        with open(LOCAL_FALLBACK_FILE, "r") as f:
            data = json.load(f)
            if data:
                return data[0]
    return {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HBase Fast Serving Loader")
    parser.add_argument("--host", default="hbase-master", help="HBase Thrift host")
    parser.add_argument("--port", type=int, default=9090, help="HBase Thrift port")
    args = parser.parse_args()

    put_serving_record(host=args.host, port=args.port)
