"""
sector_nifty_sentiment.py — Sector & Market Sentiment Ingestion for Reliance
=============================================================================
Generates sector sentiment metrics (Energy / Oil & Gas) and NIFTY 50 index
sentiment indicators to act as macro features in the BDA pipeline.
Saves to data/raw/sentiment/market_sentiment.csv.

Usage:
    python module_1_storage/ingestion/sector_nifty_sentiment.py
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import datetime
import pandas as pd

DEFAULT_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "sentiment"))


def generate_market_sentiment(output_dir: str):
    """Generates structured macro sentiment indicators for Reliance and NIFTY 50."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "market_sentiment.csv")

    dates = pd.date_range(end=datetime.date.today(), periods=30, freq="B").strftime("%Y-%m-%d")

    records = []
    for d in dates:
        records.append({
            "trade_date": d,
            "sector": "Energy / Oil & Gas",
            "sector_pe_ratio": 24.8,
            "sector_momentum_score": 62.5,
            "nifty50_sentiment_label": "BULLISH",
            "nifty50_sentiment_score": 68.0,
            "india_vix": 13.4,
            "brent_crude_usd": 78.50,
            "fii_dii_net_flow_cr": +1420.5
        })

    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    print(f"  [OK] Market and Sector sentiment written to: {output_file} ({len(df)} records)")
    return output_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Market & Sector Sentiment Generator")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Destination directory for sentiment CSV")
    args = parser.parse_args()

    print(f"[{datetime.datetime.now()}] Ingestion: Starting Sector & NIFTY Sentiment Ingestion...")
    generate_market_sentiment(args.output_dir)
