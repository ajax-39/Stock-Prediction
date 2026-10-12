"""
spark_stream_live.py — Spark Structured Streaming for High-Velocity Ticks
========================================================================
Subscribes to Kafka topic 'reliance-ticks' and aggregates live broker ticks
into 1-minute OHLCV candlestick bars using watermarked tumbling windows.
Computes the Real-Time Score (R) and writes low-latency state to HBase.

Usage:
    python module_2_processing/streaming/spark_stream_live.py [--simulated] [--ticks 20]
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

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_1_storage.hbase.hbase_loader import put_serving_record


def run_spark_structured_streaming(kafka_bootstrap: str = "kafka:9092"):
    """Initializes real Spark Structured Streaming query."""
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType

    print(f"  [STREAMING] Initializing PySpark Structured Streaming on {kafka_bootstrap}...")
    spark = SparkSession.builder \
        .appName("Reliance_Live_Tick_Stream") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
        .getOrCreate()

    schema = StructType([
        StructField("ticker", StringType()),
        StructField("timestamp", TimestampType()),
        StructField("ltp", DoubleType()),
        StructField("bid", DoubleType()),
        StructField("ask", DoubleType()),
        StructField("volume", LongType())
    ])

    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap) \
        .option("subscribe", "reliance-ticks") \
        .option("startingOffsets", "latest") \
        .load()

    df_parsed = df_kafka.select(F.from_json(F.col("value").cast("string"), schema).alias("data")).select("data.*")

    # Tumbling 1-minute window
    df_1min = df_parsed \
        .withWatermark("timestamp", "2 minutes") \
        .groupBy(F.window("timestamp", "1 minute"), "ticker") \
        .agg(
            F.first("ltp").alias("open"),
            F.max("ltp").alias("high"),
            F.min("ltp").alias("low"),
            F.last("ltp").alias("close"),
            F.sum("volume").alias("total_volume")
        )

    print("  [STREAMING] Streaming query configured.")
    return df_1min


def run_simulated_streaming_engine(tick_count: int = 15, interval: float = 0.2):
    """Zero-dependency simulation of streaming micro-batch processing."""
    print(f"  [STREAMING] Running live streaming aggregator ({tick_count} simulated ticks)...")
    base_price = 2750.0
    accumulated_vol = 0
    ticks = []

    for i in range(tick_count):
        noise = random.uniform(-0.80, 0.90)
        ltp = round(base_price + noise, 2)
        base_price = ltp
        vol = random.randint(100, 1200)
        accumulated_vol += vol

        tick = {
            "timestamp": datetime.datetime.now().isoformat(),
            "ltp": ltp,
            "volume": vol
        }
        ticks.append(tick)

        # Micro-batch calculation of Real-time Score R
        r_score = round(float(np_clip(50.0 + (noise * 12.0) + (vol / 500.0), 10.0, 95.0)), 2)

        # Update HBase fast serving layer
        put_serving_record(
            tick_data={
                "ltp": str(ltp),
                "volume": str(vol),
                "bid": str(round(ltp - 0.25, 2)),
                "ask": str(round(ltp + 0.25, 2)),
                "timestamp": tick["timestamp"]
            },
            score_data={
                "R": str(r_score)
            }
        )
        print(f"    [1-Min MicroBatch] Tick #{i+1:02d} | LTP: Rs {ltp:.2f} | Vol: {vol} | Live R-Score: {r_score}")
        time.sleep(interval)

    print(f"  [OK] Streaming cycle complete. Aggregated {accumulated_vol} volume across {tick_count} ticks.")


def np_clip(val, low, high):
    return max(low, min(high, val))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spark Live Streaming Aggregator")
    parser.add_argument("--simulated", action="store_true", default=True, help="Run standalone streaming simulator")
    parser.add_argument("--ticks", type=int, default=10, help="Number of ticks in simulated stream")
    args = parser.parse_args()

    run_simulated_streaming_engine(tick_count=args.ticks)
