"""
kaggle_ingest.py — Ingest Reliance Historical Stock Data from Kaggle
===================================================================
Downloads dataset 'muhammedshaheb/reliance-stock-data-2010-to-2025' via kagglehub,
normalizes columns, validates schemas, and saves to data/raw/prices/reliance_prices.csv.
Includes an automatic realistic fallback generator if offline or kaggle credentials missing.

Usage:
    python module_1_storage/ingestion/kaggle_ingest.py [--output-dir data/raw/prices]
"""

import os
import sys

# Windows UTF-8 console output compatibility
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import glob
import argparse
import datetime
import numpy as np
import pandas as pd

DEFAULT_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "prices"))


def generate_synthetic_reliance_data(output_file: str):
    """Fallback generator for realistic Reliance OHLCV data from 2010 to 2025."""
    print("  [WARN] Using robust fallback synthetic generator for Reliance 2010-2025 data...")
    dates = pd.bdate_range(start="2010-01-01", end="2025-12-31")
    np.random.seed(42)
    n = len(dates)

    # Simulate realistic geometric Brownian motion price series for RIL
    returns = np.random.normal(0.0006, 0.016, n)
    price_series = 500.0 * np.exp(np.cumsum(returns))

    df = pd.DataFrame({
        "Date": dates.strftime("%Y-%m-%d"),
        "Open": np.round(price_series * (1 + np.random.uniform(-0.008, 0.008, n)), 2),
        "High": np.round(price_series * (1 + np.random.uniform(0.005, 0.025, n)), 2),
        "Low": np.round(price_series * (1 - np.random.uniform(0.005, 0.025, n)), 2),
        "Close": np.round(price_series, 2),
        "Volume": np.random.randint(1_500_000, 15_000_000, n),
        "Ticker": "RELIANCE"
    })
    # Ensure High is max and Low is min
    df["High"] = np.maximum(df["High"], np.maximum(df["Open"], df["Close"]))
    df["Low"] = np.minimum(df["Low"], np.minimum(df["Open"], df["Close"]))

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"  [OK] Synthetic dataset saved to {output_file} ({len(df)} records).")
    return output_file


def download_and_process_kaggle(output_dir: str):
    """Download dataset via kagglehub and standardize schema."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "reliance_prices.csv")

    try:
        print("  [DOWNLOAD] Invoking kagglehub.dataset_download('muhammedshaheb/reliance-stock-data-2010-to-2025')...")
        import kagglehub
        path = kagglehub.dataset_download("muhammedshaheb/reliance-stock-data-2010-to-2025")
        print(f"  [PACKAGE] Kaggle files downloaded to: {path}")

        csv_files = glob.glob(os.path.join(path, "*.csv"))
        if not csv_files:
            csv_files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)

        if not csv_files:
            print("  [WARN] No CSV files found inside downloaded path.")
            return generate_synthetic_reliance_data(output_file)

        target_csv = csv_files[0]
        print(f"  [FILE] Reading source CSV: {target_csv}")
        df = pd.read_csv(target_csv)

        # Standardize column naming
        col_map = {}
        for c in df.columns:
            clean_c = c.strip().lower()
            if "date" in clean_c:
                col_map[c] = "Date"
            elif clean_c == "open" or "open" in clean_c:
                col_map[c] = "Open"
            elif clean_c == "high" or "high" in clean_c:
                col_map[c] = "High"
            elif clean_c == "low" or "low" in clean_c:
                col_map[c] = "Low"
            elif clean_c in ["close", "adj close", "closing"]:
                col_map[c] = "Close"
            elif "volume" in clean_c or "vol" in clean_c:
                col_map[c] = "Volume"

        df = df.rename(columns=col_map)
        required_cols = ["Date", "Open", "High", "Low", "Close", "Volume"]

        for req in required_cols:
            if req not in df.columns:
                print(f"  [WARN] Missing required column: {req}. Falling back.")
                return generate_synthetic_reliance_data(output_file)

        df = df[required_cols].copy()
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        df["Ticker"] = "RELIANCE"
        df = df.sort_values("Date").drop_duplicates(subset=["Date"])

        df.to_csv(output_file, index=False)
        print(f"  [SUCCESS] Normalized and saved Kaggle data to: {output_file} ({len(df)} rows)")
        return output_file

    except Exception as e:
        print(f"  [WARN] Kaggle download could not proceed directly ({e}). Initiating fallback.")
        return generate_synthetic_reliance_data(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kaggle Reliance stock data downloader")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Destination directory for raw price data")
    args = parser.parse_args()

    print(f"[{datetime.datetime.now()}] Ingestion: Starting Reliance Kaggle Ingest...")
    download_and_process_kaggle(args.output_dir)
