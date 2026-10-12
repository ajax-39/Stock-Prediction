#!/usr/bin/env python3
"""
sector_momentum_mapper.py — Hadoop Streaming Mapper for Rolling Momentum
========================================================================
Reads cleaned Reliance trading rows from stdin and outputs:
    RELIANCE \\t trade_date,close_price,volume
"""

import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def mapper():
    for line in sys.stdin:
        line = line.strip()
        if not line or line.startswith("trade_date") or line.startswith("Date"):
            continue

        parts = line.split(",")
        if len(parts) >= 6:
            trade_date = parts[0].strip()
            close_price = parts[4].strip()
            volume = parts[5].strip()
            ticker = parts[6].strip() if len(parts) > 6 else "RELIANCE"

            # Key: Ticker, Value: Date,Close,Volume
            print(f"{ticker}\t{trade_date},{close_price},{volume}")


if __name__ == "__main__":
    mapper()
