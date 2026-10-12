"""
upload_to_hdfs.py — Upload Ingested Datasets to HDFS Data Lake
=============================================================
Transfers staged raw CSV files (prices, news, sentiment) to the HDFS raw zone.
Supports standard HDFS CLI commands as well as WebHDFS HTTP REST API.

Usage:
    python module_1_storage/hdfs/upload_to_hdfs.py [--webhdfs-host hadoop-master]
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import glob
import argparse
import subprocess
import requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

UPLOAD_MAPPINGS = [
    {
        "local_src": os.path.join(PROJECT_ROOT, "data", "raw", "prices", "reliance_prices.csv"),
        "hdfs_dst": "/bda/lake/raw/prices/reliance_prices.csv",
        "hdfs_dir": "/bda/lake/raw/prices"
    },
    {
        "local_src": os.path.join(PROJECT_ROOT, "data", "raw", "news", "reliance_news.csv"),
        "hdfs_dst": "/bda/lake/raw/news/reliance_news.csv",
        "hdfs_dir": "/bda/lake/raw/news"
    },
    {
        "local_src": os.path.join(PROJECT_ROOT, "data", "raw", "sentiment", "market_sentiment.csv"),
        "hdfs_dst": "/bda/lake/raw/sentiment/market_sentiment.csv",
        "hdfs_dir": "/bda/lake/raw/sentiment"
    }
]


def upload_via_cli(local_file: str, hdfs_dir: str):
    """Executes 'hdfs dfs -put' using the local hadoop binary."""
    try:
        subprocess.run(["hdfs", "dfs", "-mkdir", "-p", hdfs_dir], check=True, capture_output=True)
        cmd = ["hdfs", "dfs", "-put", "-f", local_file, hdfs_dir]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  [HDFS-CLI] Uploaded {os.path.basename(local_file)} -> {hdfs_dir}")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def upload_via_webhdfs(local_file: str, hdfs_path: str, host: str = "hadoop-master", port: int = 9870):
    """Uploads file using WebHDFS REST API (useful when running outside container)."""
    url = f"http://{host}:{port}/webhdfs/v1{hdfs_path}?op=CREATE&overwrite=true&noredirect=true"
    try:
        resp = requests.put(url, timeout=5)
        if resp.status_code == 200:
            datanode_url = resp.json().get("Location")
            if datanode_url:
                with open(local_file, "rb") as f:
                    put_resp = requests.put(datanode_url, data=f, timeout=30)
                if put_resp.status_code in [200, 201]:
                    print(f"  [WebHDFS] Uploaded {os.path.basename(local_file)} -> {hdfs_path}")
                    return True
    except Exception:
        pass
    return False


def run_uploads(webhdfs_host: str):
    print("  [HDFS] Initiating HDFS Data Lake synchronization...")
    for item in UPLOAD_MAPPINGS:
        local_src = item["local_src"]
        hdfs_dir = item["hdfs_dir"]
        hdfs_dst = item["hdfs_dst"]

        if not os.path.exists(local_src):
            print(f"  [WARN] Staged file missing: {local_src}. Run ingestion scripts first.")
            continue

        success = upload_via_cli(local_src, hdfs_dir)
        if not success:
            success = upload_via_webhdfs(local_src, hdfs_dst, host=webhdfs_host)

        if not success:
            print(f"  [INFO] Notice: HDFS daemon not reached. Local staging file maintained for standalone pipeline.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HDFS Uploader for Reliance Data")
    parser.add_argument("--webhdfs-host", default="hadoop-master", help="Hostname for WebHDFS service")
    args = parser.parse_args()

    run_uploads(args.webhdfs_host)
