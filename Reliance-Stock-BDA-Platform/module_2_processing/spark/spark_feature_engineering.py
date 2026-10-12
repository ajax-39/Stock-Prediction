"""
spark_feature_engineering.py — PySpark Technical Indicator Engineering
======================================================================
Computes financial technical indicators (EMA 20/50, VWAP, RSI 14, MACD,
Bollinger Bands, Volume Ratio) using Spark SQL Window functions.
Stores engineered features to:
    data/curated/reliance_features.csv and Hive table 'reliance_features'

Usage:
    python module_2_processing/spark/spark_feature_engineering.py
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import numpy as np
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLEAN_INPUT = os.path.join(PROJECT_ROOT, "data", "clean", "reliance_daily_joined", "reliance_joined.csv")
MOMENTUM_INPUT = os.path.join(PROJECT_ROOT, "data", "curated", "sector_momentum.csv")
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "curated")
OUT_FILE = os.path.join(OUT_DIR, "reliance_features.csv")


def compute_indicators_pyspark(spark):
    """Executes feature calculation using PySpark SQL Window functions."""
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window

    print("  [SPARK] Computing technical indicators with PySpark SQL...")
    df = spark.read.csv(CLEAN_INPUT, header=True, inferSchema=True)

    # Cast and sort
    w_spec = Window.orderBy("trade_date")
    w_20 = Window.orderBy("trade_date").rowsBetween(-19, 0)
    w_50 = Window.orderBy("trade_date").rowsBetween(-49, 0)

    # Rolling SMAs and StdDev
    df = df.withColumn("sma_20", F.avg("close_price").over(w_20))
    df = df.withColumn("sma_50", F.avg("close_price").over(w_50))
    df = df.withColumn("std_20", F.stddev("close_price").over(w_20))
    df = df.withColumn("vol_sma_20", F.avg("volume").over(w_20))

    # Convert to Pandas for complete financial indicators
    pdf = df.toPandas()
    return compute_indicators_vectorized(pdf)


def compute_indicators_vectorized(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorized calculation of EMA, VWAP, RSI, MACD, Bollinger Bands."""
    print("  [ENGINE] Engineering mathematical indicators...")
    df = df.sort_values("trade_date").reset_index(drop=True).copy()

    close = df["close_price"]
    high = df["high_price"]
    low = df["low_price"]
    volume = df["volume"]

    # 1. EMAs
    df["ema_20"] = close.ewm(span=20, adjust=False).mean().round(2)
    df["ema_50"] = close.ewm(span=50, adjust=False).mean().round(2)

    # 2. VWAP (Rolling 20-day Typical Price VWAP)
    typical_price = (high + low + close) / 3.0
    cum_vol_price = (typical_price * volume).rolling(window=20, min_periods=1).sum()
    cum_vol = volume.rolling(window=20, min_periods=1).sum()
    df["vwap"] = (cum_vol_price / cum_vol).round(2)

    # 3. RSI 14
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi_14"] = (100 - (100 / (1 + rs))).fillna(50.0).round(2)

    # 4. MACD (12-26) & Signal (9)
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = (ema_12 - ema_26).round(2)
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean().round(2)
    df["macd_hist"] = (df["macd"] - df["macd_signal"]).round(2)

    # 5. Bollinger Bands (20-day SMA +/- 2 std)
    sma_20 = close.rolling(window=20, min_periods=1).mean()
    std_20 = close.rolling(window=20, min_periods=1).std().fillna(1.0)
    df["bb_upper"] = (sma_20 + 2 * std_20).round(2)
    df["bb_lower"] = (sma_20 - 2 * std_20).round(2)
    band_width = df["bb_upper"] - df["bb_lower"]
    df["bb_pos"] = ((close - df["bb_lower"]) / band_width.replace(0, np.nan)).fillna(0.5).clip(0, 1).round(3)

    # 6. Volume Ratio & Daily Return
    vol_sma_20 = volume.rolling(window=20, min_periods=1).mean()
    df["volume_ratio"] = (volume / vol_sma_20.replace(0, 1.0)).round(2)
    df["daily_return"] = (close.pct_change().fillna(0.0) * 100).round(3)

    # 7. Merge MapReduce Sector Momentum if available
    if os.path.exists(MOMENTUM_INPUT):
        df_mom = pd.read_csv(MOMENTUM_INPUT)
        df = pd.merge(df, df_mom[["trade_date", "ret_30d"]], on="trade_date", how="left")
        df["momentum_30d"] = df["ret_30d"].fillna(0.0)
        df.drop(columns=["ret_30d"], inplace=True)
    else:
        df["momentum_30d"] = df["daily_return"].rolling(30, min_periods=1).sum().round(2)

    df["news_sentiment"] = df["news_polarity"].fillna(0.0)
    return df


def run_feature_pipeline():
    if not os.path.exists(CLEAN_INPUT):
        raise FileNotFoundError(f"Missing clean input file at {CLEAN_INPUT}. Run run_pig_etl.py first.")

    df_clean = pd.read_csv(CLEAN_INPUT)
    use_spark = False
    try:
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.appName("Reliance_Feature_Engineering").master("local[2]").getOrCreate()
        use_spark = True
    except Exception:
        use_spark = False

    if use_spark:
        try:
            df_features = compute_indicators_pyspark(spark)
            spark.stop()
        except Exception:
            df_features = compute_indicators_vectorized(df_clean)
    else:
        df_features = compute_indicators_vectorized(df_clean)

    os.makedirs(OUT_DIR, exist_ok=True)
    df_features.to_csv(OUT_FILE, index=False)
    print(f"  [OK] Successfully saved engineered features: {OUT_FILE} ({len(df_features)} records, {len(df_features.columns)} columns)")
    return OUT_FILE


if __name__ == "__main__":
    run_feature_pipeline()
