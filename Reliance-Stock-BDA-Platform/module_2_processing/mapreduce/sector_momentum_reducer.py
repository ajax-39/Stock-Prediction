#!/usr/bin/env python3
"""
sector_momentum_reducer.py — Hadoop Streaming Reducer for Rolling Momentum
==========================================================================
Aggregates time-series records for RELIANCE, calculates rolling 30/60/90-day
price momentum percentages and volume moving averages.
Emits tab-delimited values:
    trade_date \\t ticker \\t ret_30d \\t ret_60d \\t ret_90d \\t vol_trend
"""

import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def reducer():
    current_ticker = None
    records = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) != 2:
            continue

        ticker, val = parts
        val_parts = val.split(",")
        if len(val_parts) != 3:
            continue

        trade_date = val_parts[0]
        try:
            close_price = float(val_parts[1])
            volume = float(val_parts[2])
        except ValueError:
            continue

        if current_ticker and ticker != current_ticker:
            process_ticker_series(current_ticker, records)
            records = []

        current_ticker = ticker
        records.append((trade_date, close_price, volume))

    if current_ticker and records:
        process_ticker_series(current_ticker, records)


def process_ticker_series(ticker, records):
    """Sorts chronologically and calculates rolling momentum windows."""
    records.sort(key=lambda x: x[0])
    n = len(records)

    for i in range(n):
        trade_date, close, vol = records[i]

        # 30-day return
        ret_30d = 0.0
        if i >= 30:
            past_close = records[i - 30][1]
            if past_close > 0:
                ret_30d = round(((close - past_close) / past_close) * 100, 2)

        # 60-day return
        ret_60d = 0.0
        if i >= 60:
            past_close = records[i - 60][1]
            if past_close > 0:
                ret_60d = round(((close - past_close) / past_close) * 100, 2)

        # 90-day return
        ret_90d = 0.0
        if i >= 90:
            past_close = records[i - 90][1]
            if past_close > 0:
                ret_90d = round(((close - past_close) / past_close) * 100, 2)

        # 20-day Volume moving average comparison
        vol_ratio = 1.0
        if i >= 20:
            vols = [r[2] for r in records[i - 20:i]]
            avg_vol = sum(vols) / len(vols) if vols else 1.0
            if avg_vol > 0:
                vol_ratio = round(vol / avg_vol, 2)

        print(f"{trade_date}\t{ticker}\t{ret_30d}\t{ret_60d}\t{ret_90d}\t{vol_ratio}")


if __name__ == "__main__":
    reducer()
