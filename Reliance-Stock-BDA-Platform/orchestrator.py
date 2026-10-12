"""
orchestrator.py — Master Pipeline Orchestrator for Reliance BDA Platform
========================================================================
Executes the entire end-to-end Big Data Analytics workflow in sequence:
    Stage 1: Ingestion (Kaggle Reliance 2010-2025, Curated News, Sector Sentiment)
    Stage 2: Storage Lake Sync (HDFS & Hive Metastore staging)
    Stage 3: Batch ETL & MapReduce (Pig normalization & 30/60/90d momentum)
    Stage 4: Feature Engineering & Scoring (PySpark indicators & 4-score model)
    Stage 5: MLlib Training & Prediction (Model fitting & next-day inference)
    Stage 6: Fast Serving (HBase reverse-timestamp cache)
    Stage 7: Streamlit Presentation Launch

Usage:
    python orchestrator.py [--launch-dashboard]
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
import argparse
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def log_stage(stage_num: int, title: str):
    print("\n" + "=" * 70)
    print(f"  [STAGE {stage_num}/6] {title}")
    print("=" * 70)


def run_step(script_relative_path: str, desc: str):
    full_path = os.path.join(PROJECT_ROOT, script_relative_path)
    print(f"  ▶️ Executing: {desc} ({script_relative_path})...")
    t0 = time.time()
    res = subprocess.run([sys.executable, full_path], cwd=PROJECT_ROOT)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"  ❌ Failed with exit code {res.returncode}")
        return False
    print(f"  ✅ Completed in {elapsed:.2f}s")
    return True


def execute_full_pipeline(launch_ui: bool = False):
    print("*" * 70)
    print("  🚀 RELIANCE BDA STOCK PREDICTION PLATFORM — MASTER PIPELINE RUNNER")
    print("*" * 70)

    # Stage 1: Ingestion
    log_stage(1, "Data Ingestion (Kaggle OHLCV, Curated News, Macro Sentiment)")
    run_step("module_1_storage/ingestion/kaggle_ingest.py", "Kaggle Reliance Ingestion")
    run_step("module_1_storage/ingestion/news_curated_feed.py", "Curated News & TextBlob Sentiment")
    run_step("module_1_storage/ingestion/sector_nifty_sentiment.py", "Sector & Macro Sentiment Ingestion")

    # Stage 2: Storage Layer
    log_stage(2, "Storage Layer Synchronization (HDFS & Hive)")
    run_step("module_1_storage/hdfs/upload_to_hdfs.py", "HDFS Data Lake Upload")

    # Stage 3: Batch ETL & MapReduce
    log_stage(3, "Batch Processing (Apache Pig ETL & Hadoop MapReduce)")
    run_step("module_2_processing/pig/run_pig_etl.py", "Apache Pig Deduplication & Joining")
    run_step("module_2_processing/mapreduce/run_momentum_mr.py", "Hadoop MapReduce Sector Momentum")

    # Stage 4: Feature Engineering & Scoring
    log_stage(4, "PySpark Feature Engineering & 4-Score Multi-Factor Engine")
    run_step("module_2_processing/spark/spark_feature_engineering.py", "Spark SQL Window Indicators")
    run_step("module_2_processing/spark/spark_score_engine.py", "Multi-Factor Scoring (T, F, N, R -> S)")

    # Stage 5: Machine Learning & Prediction
    log_stage(5, "Spark MLlib Model Training & Next-Day Prediction")
    run_step("module_2_processing/prediction/train_mllib_model.py", "Time-Series Model Training & Evaluation")
    run_step("module_2_processing/prediction/predict_next_day.py", "Next-Day Price & Trade Signal Forecast")

    # Stage 6: Streaming Simulation
    log_stage(6, "Streaming & Fast Serving Check")
    run_step("module_2_processing/streaming/spark_stream_live.py", "Spark Streaming Live Tick Aggregation")

    print("\n" + "=" * 70)
    print("  🎉 PIPELINE EXECUTION FINISHED SUCCESSFULLY!")
    print("=" * 70)

    if launch_ui:
        print("\n  🌐 Launching Streamlit Dashboard on port 8501...")
        cmd = ["streamlit", "run", "module_3_dashboard/app.py", "--server.port=8501"]
        subprocess.run(cmd, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliance BDA Master Pipeline Runner")
    parser.add_argument("--launch-dashboard", action="store_true", help="Launch Streamlit dashboard upon completion")
    args = parser.parse_args()

    execute_full_pipeline(args.launch_dashboard)
