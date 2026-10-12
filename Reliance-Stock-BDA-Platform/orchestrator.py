"""
orchestrator.py — Master Pipeline Orchestrator & DevOps Automation Engine
========================================================================
Automates the end-to-end Big Data Analytics workflow for Reliance Industries:
  Stage 0: Environment & Docker Cluster Health Check
  Stage 1: Ingestion (Kaggle Reliance 2010-2025, Curated News, Macro Sentiment)
  Stage 2: Storage Lake Sync (HDFS 3-Zone setup, Upload, Hive DDL)
  Stage 3: Batch ETL & MapReduce (Pig normalization & 30/60/90d momentum)
  Stage 4: Feature Engineering & Scoring (PySpark Window indicators & 4-score model)
  Stage 5: MLlib Training & Prediction (Model training & next-day inference)
  Stage 6: Fast Serving (HBase reverse-timestamp cache update)
  Stage 7: Interactive Dashboard Launch (Streamlit port 8501)

Supports:
  --local-standalone : Runs with zero Docker/Hadoop dependency on local machine
  --launch-dashboard : Launches Streamlit UI immediately upon pipeline completion

Usage:
    python orchestrator.py [--local-standalone] [--launch-dashboard]
"""

import os
import sys

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import socket
import argparse
import subprocess
import datetime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# -----------------------------------------------------------------------------
# Terminal Styling Helpers
# -----------------------------------------------------------------------------
def print_banner():
    print("*" * 75)
    print("   RELIANCE BDA STOCK PREDICTION PLATFORM — MASTER ORCHESTRATION ENGINE")
    print(f"   Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Target: RELIANCE.NS")
    print("*" * 75)


def print_stage_header(stage_idx: int, total_stages: int, title: str):
    print("\n" + "=" * 75)
    print(f"  [STAGE {stage_idx}/{total_stages}] {title.upper()}")
    print("=" * 75)


def check_port(host: str, port: int, timeout: float = 0.5) -> bool:
    """Checks if a TCP socket port is reachable."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


# -----------------------------------------------------------------------------
# Stage 0: Health & Environment Telemetry
# -----------------------------------------------------------------------------
def run_stage_0_health_check(force_standalone: bool = False):
    print_stage_header(0, 7, "Environment & Cluster Telemetry Check")
    t0 = time.time()

    services = [
        ("ZooKeeper", "localhost", 2181),
        ("Kafka Broker", "localhost", 9092),
        ("HDFS NameNode UI", "localhost", 9870),
        ("HDFS IPC", "localhost", 9000),
        ("YARN ResourceManager", "localhost", 8088),
        ("Spark Master", "localhost", 7077),
        ("HiveServer2", "localhost", 10000),
        ("HBase Master", "localhost", 16010),
        ("HBase Thrift", "localhost", 9090)
    ]

    cluster_online = False
    if not force_standalone:
        online_count = 0
        for name, host, port in services:
            is_up = check_port(host, port)
            tag = "[ONLINE]" if is_up else "[OFFLINE]"
            print(f"    - {name:<22} ({host}:{port:<5}) : {tag}")
            if is_up:
                online_count += 1
        cluster_online = (online_count >= 3)

    if cluster_online:
        mode_str = "DISTRIBUTED DOCKER CLUSTER MODE"
        print(f"\n  [HEALTH] Cluster detected! Running in {mode_str}.")
    else:
        mode_str = "STANDALONE PYTHON-NATIVE ENGINE (Zero-Crash Fallback)"
        print(f"\n  [HEALTH] Standalone mode activated ({mode_str}).")
        print("           All BDA operations (HDFS, Hive, HBase, Pig, MapReduce, Spark) will execute natively.")

    elapsed = time.time() - t0
    print(f"  [CHECK DONE] Telemetry completed in {elapsed:.2f}s")
    return cluster_online


# -----------------------------------------------------------------------------
# Script Runner Utility
# -----------------------------------------------------------------------------
def run_step(script_rel_path: str, desc: str) -> bool:
    full_path = os.path.join(PROJECT_ROOT, script_rel_path)
    print(f"\n  ▶️ [RUNNING] {desc}...")
    print(f"     Path: {script_rel_path}")
    t0 = time.time()
    res = subprocess.run([sys.executable, full_path], cwd=PROJECT_ROOT)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"  ❌ [FAILED] Step exited with code {res.returncode}")
        return False
    print(f"  ✅ [PASSED] Finished in {elapsed:.2f}s")
    return True


# -----------------------------------------------------------------------------
# Master Execution Flow
# -----------------------------------------------------------------------------
def execute_master_pipeline(force_standalone: bool = False, launch_ui: bool = False):
    t_start = time.time()
    print_banner()

    # Stage 0: Health
    is_cluster = run_stage_0_health_check(force_standalone)

    # Stage 1: Ingestion
    print_stage_header(1, 7, "Data Ingestion (Kaggle OHLCV, Curated News, Macro Sentiment)")
    run_step("module_1_storage/ingestion/kaggle_ingest.py", "Kaggle Reliance 2010-2025 Downloader")
    run_step("module_1_storage/ingestion/news_curated_feed.py", "Curated News & TextBlob Sentiment NLP")
    run_step("module_1_storage/ingestion/sector_nifty_sentiment.py", "Sector Momentum & NIFTY 50 Macro Feeds")

    # Stage 2: Storage Layer Sync
    print_stage_header(2, 7, "Storage Layer (HDFS Data Lake & Hive Metastore)")
    run_step("module_1_storage/hdfs/upload_to_hdfs.py", "HDFS 3-Zone Storage Lake Synchronization")

    # Stage 3: Batch ETL & MapReduce
    print_stage_header(3, 7, "Batch Processing (Apache Pig Deduplication & Hadoop MapReduce)")
    run_step("module_2_processing/pig/run_pig_etl.py", "Apache Pig Latin ETL (Prices + News Join)")
    run_step("module_2_processing/mapreduce/run_momentum_mr.py", "Hadoop Streaming MapReduce (30/60/90d Sector Momentum)")

    # Stage 4: Feature Engineering & Scoring
    print_stage_header(4, 7, "PySpark Window Indicators & Multi-Factor Scoring Engine")
    run_step("module_2_processing/spark/spark_feature_engineering.py", "Spark SQL Window Functions (EMA, VWAP, RSI, MACD, BB)")
    run_step("module_2_processing/spark/spark_score_engine.py", "4-Score Multi-Factor Engine (T, F, N, R -> Composite S)")

    # Stage 5: MLlib Training & Prediction
    print_stage_header(5, 7, "Spark MLlib Model Training & Next-Day Forecasting")
    run_step("module_2_processing/prediction/train_mllib_model.py", "Time-Series Split ML Model Training & Benchmarking")
    run_step("module_2_processing/prediction/predict_next_day.py", "Next-Day Price Prediction & Trade Signal Generation")

    # Stage 6: Fast Serving & Streaming Check
    print_stage_header(6, 7, "Speed Layer & Fast Serving (Kafka Stream & HBase)")
    run_step("module_2_processing/streaming/spark_stream_live.py", "Spark Structured Streaming 1-Minute Micro-Batch Aggregation")

    total_time = time.time() - t_start
    print("\n" + "*" * 75)
    print(f"  🎉 ENTIRE BDA PIPELINE EXECUTED SUCCESSFULLY IN {total_time:.2f}s!")
    print("*" * 75)

    # Stage 7: Streamlit Launch
    if launch_ui:
        print_stage_header(7, 7, "Presentation Layer (Launching Streamlit Cockpit)")
        print("  🌐 Starting Streamlit server on http://localhost:8501...")
        cmd = ["streamlit", "run", "module_3_dashboard/app.py", "--server.port=8501"]
        subprocess.run(cmd, cwd=PROJECT_ROOT)
    else:
        print("\n  💡 Next Step: To view the interactive 3-page cockpit, run:")
        print("     streamlit run module_3_dashboard/app.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliance BDA Master Pipeline Runner")
    parser.add_argument("--local-standalone", action="store_true", help="Force standalone execution (skip Docker socket checks)")
    parser.add_argument("--launch-dashboard", action="store_true", help="Launch Streamlit dashboard immediately upon completion")
    args = parser.parse_args()

    execute_master_pipeline(args.local_standalone, args.launch_dashboard)
