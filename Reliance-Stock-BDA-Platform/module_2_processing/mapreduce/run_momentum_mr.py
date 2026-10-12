"""
run_momentum_mr.py — Local Streaming & Verification Runner for MapReduce
=========================================================================
Runs mapper | sort | reducer workflow locally using standard streams,
validating the MapReduce logic and persisting output to:
    data/curated/sector_momentum.csv

Usage:
    python module_2_processing/mapreduce/run_momentum_mr.py
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
CLEAN_INPUT = os.path.join(PROJECT_ROOT, "data", "clean", "reliance_daily_joined", "reliance_joined.csv")
OUT_DIR = os.path.join(PROJECT_ROOT, "data", "curated")
OUT_FILE = os.path.join(OUT_DIR, "sector_momentum.csv")

MAPPER_SCRIPT = os.path.join(os.path.dirname(__file__), "sector_momentum_mapper.py")
REDUCER_SCRIPT = os.path.join(os.path.dirname(__file__), "sector_momentum_reducer.py")


def run_local_mapreduce_pipeline():
    print("  [MAPREDUCE] Running Sector Momentum Hadoop Streaming job...")
    if not os.path.exists(CLEAN_INPUT):
        raise FileNotFoundError(f"Missing clean joined data at {CLEAN_INPUT}. Run run_pig_etl.py first.")

    # Execute mapper
    with open(CLEAN_INPUT, "r", encoding="utf-8") as f_in:
        p_map = subprocess.Popen([sys.executable, MAPPER_SCRIPT], stdin=f_in, stdout=subprocess.PIPE, text=True)
        # Execute reducer
        p_red = subprocess.Popen([sys.executable, REDUCER_SCRIPT], stdin=p_map.stdout, stdout=subprocess.PIPE, text=True)
        p_map.stdout.close()
        output, _ = p_red.communicate()

    # Parse reducer output into DataFrame
    lines = [line.strip().split("\t") for line in output.strip().split("\n") if line.strip()]
    if not lines or len(lines[0]) < 6:
        print("  [WARN] MapReduce produced empty output.")
        return None

    df_mr = pd.DataFrame(lines, columns=["trade_date", "ticker", "ret_30d", "ret_60d", "ret_90d", "vol_trend"])
    df_mr["ret_30d"] = df_mr["ret_30d"].astype(float)
    df_mr["ret_60d"] = df_mr["ret_60d"].astype(float)
    df_mr["ret_90d"] = df_mr["ret_90d"].astype(float)
    df_mr["vol_trend"] = df_mr["vol_trend"].astype(float)

    os.makedirs(OUT_DIR, exist_ok=True)
    df_mr.to_csv(OUT_FILE, index=False)
    print(f"  [OK] MapReduce output saved: {OUT_FILE} ({len(df_mr)} records)")
    return OUT_FILE


if __name__ == "__main__":
    run_local_mapreduce_pipeline()
