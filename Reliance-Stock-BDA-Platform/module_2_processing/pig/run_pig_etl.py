"""
run_pig_etl.py — Runner & Standalone Fallback for Pig Batch ETL
==============================================================
Executes Apache Pig ETL on cluster or provides an identical local fallback
that deduplicates, normalizes, and left-joins price and news data.
Outputs to:
    data/clean/reliance_daily_joined/reliance_joined.csv

Usage:
    python module_2_processing/pig/run_pig_etl.py
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import subprocess
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW_PRICES = os.path.join(PROJECT_ROOT, "data", "raw", "prices", "reliance_prices.csv")
RAW_NEWS = os.path.join(PROJECT_ROOT, "data", "raw", "news", "reliance_news.csv")
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "clean", "reliance_daily_joined")
OUT_FILE = os.path.join(OUT_DIR, "reliance_joined.csv")


def run_pig_cluster():
    """Attempts to run pig on Hadoop cluster."""
    pig_script = os.path.join(os.path.dirname(__file__), "etl_normalize_join.pig")
    try:
        res = subprocess.run(["pig", "-f", pig_script], capture_output=True, text=True, timeout=60)
        if res.returncode == 0:
            print("  [PIG] Cluster Pig ETL completed successfully.")
            return True
    except Exception:
        pass
    return False


def run_standalone_pig_etl():
    """Python simulation replicating the exact Pig Latin pipeline."""
    print("  [PIG-ETL] Running ETL normalization & join pipeline...")
    if not os.path.exists(RAW_PRICES):
        raise FileNotFoundError(f"Missing raw prices at {RAW_PRICES}. Run kaggle_ingest.py first.")

    df_prices = pd.read_csv(RAW_PRICES)
    # 1. Cleanse & normalize prices
    df_prices["trade_date"] = pd.to_datetime(df_prices["Date"]).dt.strftime("%Y-%m-%d")
    df_prices["open_price"] = df_prices["Open"].astype(float)
    df_prices["high_price"] = df_prices["High"].astype(float)
    df_prices["low_price"] = df_prices["Low"].astype(float)
    df_prices["close_price"] = df_prices["Close"].astype(float)
    df_prices["volume"] = df_prices["Volume"].astype(int)
    df_prices["ticker"] = "RELIANCE"

    # Deduplicate by trade_date keeping highest volume
    df_prices = df_prices.sort_values("volume", ascending=False).drop_duplicates(subset=["trade_date"])
    df_prices = df_prices.sort_values("trade_date").reset_index(drop=True)

    # 2. Cleanse news
    df_news = pd.DataFrame()
    if os.path.exists(RAW_NEWS):
        df_news = pd.read_csv(RAW_NEWS)
        df_news["trade_date"] = pd.to_datetime(df_news["trade_date"]).dt.strftime("%Y-%m-%d")
        df_news = df_news.drop_duplicates(subset=["trade_date"])

    # 3. Left Join
    if not df_news.empty:
        news_cols = ["trade_date", "polarity_score", "sentiment_label"]
        df_joined = pd.merge(df_prices, df_news[news_cols], on="trade_date", how="left")
        df_joined["news_polarity"] = df_joined["polarity_score"].fillna(0.0)
        df_joined["sentiment_label"] = df_joined["sentiment_label"].fillna("NEUTRAL")
    else:
        df_joined = df_prices.copy()
        df_joined["news_polarity"] = 0.0
        df_joined["sentiment_label"] = "NEUTRAL"

    cols = ["trade_date", "open_price", "high_price", "low_price", "close_price", "volume", "ticker", "news_polarity", "sentiment_label"]
    df_clean = df_joined[cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    df_clean.to_csv(OUT_FILE, index=False)
    print(f"  [OK] Stored cleaned & joined records: {OUT_FILE} ({len(df_clean)} rows)")
    return OUT_FILE


if __name__ == "__main__":
    if not run_pig_cluster():
        run_standalone_pig_etl()
