"""
run.py — Single Master Terminal Launcher for Reliance BDA Platform
==================================================================
Runs the complete Big Data Analytics project with a single command from your terminal:
    1. Verifies Python dependencies.
    2. Executes full BDA data pipeline (Kaggle Ingest -> Pig ETL -> MapReduce -> Spark -> MLlib).
    3. Generates next-day stock price prediction and trading signals for RELIANCE.
    4. Automatically launches the interactive Streamlit Cockpit on http://localhost:8501.

Usage:
    python run.py                     (runs complete 7-stage pipeline then opens UI)
    python run.py --dashboard-only    (launches UI immediately using cached artifacts)
    python run.py --pipeline-only     (runs data & ML pipeline without launching UI)
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
import argparse
import subprocess
import webbrowser

# Resolve project root whether executed from workspace root or platform directory
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
if os.path.exists(os.path.join(CURRENT_DIR, "module_3_dashboard")):
    PROJECT_ROOT = CURRENT_DIR
else:
    PROJECT_ROOT = os.path.join(CURRENT_DIR, "Reliance-Stock-BDA-Platform")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def check_and_install_dependencies():
    """Verifies critical packages and installs them if missing."""
    required = ["streamlit", "plotly", "pandas", "numpy"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"  [SETUP] Installing missing packages: {', '.join(missing)}...")
        subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=True)
        print("  [SETUP] Dependencies installed successfully.")


def run_pipeline():
    """Executes the master pipeline orchestrator."""
    orchestrator_script = os.path.join(PROJECT_ROOT, "orchestrator.py")
    print("\n" + "=" * 75)
    print("  🚀 EXECUTING COMPLETE 7-STAGE BDA DATA & ML PIPELINE")
    print("=" * 75)
    print("  Stages to be executed:")
    print("    • Stage 0: Environment & Cluster Telemetry Check")
    print("    • Stage 1: Data Ingestion (Kaggle OHLCV, News NLP, Macro Sentiment)")
    print("    • Stage 2: HDFS Storage Layer (Raw, Staged, Curated Zones)")
    print("    • Stage 3: Apache Pig ETL & Hadoop MapReduce Processing")
    print("    • Stage 4: PySpark Window Indicator Calculation & 4-Score Multi-Factor Engine")
    print("    • Stage 5: Spark MLlib Model Training & Next-Day Forecasting")
    print("    • Stage 6: Speed Layer Streaming Aggregation & HBase Mock")
    print("  ⏱️  Total Pipeline Runtime: ~45 to 50 seconds")
    print("  🌐 Note: Port 8501 and your browser will automatically open once all stages finish.")
    print("=" * 75 + "\n")
    t0 = time.time()
    res = subprocess.run([sys.executable, orchestrator_script, "--local-standalone"], cwd=PROJECT_ROOT)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"\n❌ Pipeline execution encountered an error (exit code: {res.returncode})")
        sys.exit(res.returncode)
    print(f"\n✅ All 7 BDA Stages completed successfully in {elapsed:.2f}s!")


def _ensure_streamlit_credentials():
    """Ensures Streamlit credentials exist to prevent interactive onboarding prompts."""
    for base in [PROJECT_ROOT, CURRENT_DIR, os.path.expanduser("~")]:
        try:
            s_dir = os.path.join(base, ".streamlit")
            os.makedirs(s_dir, exist_ok=True)
            c_file = os.path.join(s_dir, "credentials.toml")
            if not os.path.exists(c_file):
                with open(c_file, "w", encoding="utf-8") as f:
                    f.write('[general]\nemail = ""\n')
        except Exception:
            pass


def launch_dashboard():
    """Launches the Streamlit presentation dashboard and opens browser once port is ready."""
    import socket
    import threading

    _ensure_streamlit_credentials()

    app_script = os.path.join(PROJECT_ROOT, "module_3_dashboard", "app.py")
    port = 8501
    host = "localhost"
    url = f"http://{host}:{port}"

    print("\n" + "=" * 75)
    print(f"  🌐 LAUNCHING STREAMLIT PRESENTATION COCKPIT ON {url}")
    print("=" * 75)
    print(f"  - App entrypoint: {app_script}")
    print(f"  - URL: {url}")
    print("  - Waiting for HTTP server socket to become live before opening browser...")
    print("  - Press CTRL+C in this terminal window to stop the server at any time.\n")

    def wait_and_open_browser(target_host, target_port, timeout=45):
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)
                    if sock.connect_ex((target_host, target_port)) == 0:
                        print(f"\n  ✅ [PORT {target_port} ACTIVE] Streamlit server is listening!")
                        print(f"  🚀 Launching browser: {url}\n")
                        time.sleep(0.5)
                        webbrowser.open(url)
                        return
            except Exception:
                pass
            time.sleep(0.4)
        print(f"\n  ⚠️ Port {target_port} health check timed out. Please visit {url} manually in your browser.")

    threading.Thread(target=wait_and_open_browser, args=(host, port), daemon=True).start()

    # Pass environment variables and flags to guarantee headless execution without prompts
    env = os.environ.copy()
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    cmd = [
        sys.executable, "-m", "streamlit", "run", app_script,
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]
    try:
        subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
    except KeyboardInterrupt:
        print("\n  🛑 Dashboard server stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="Master Terminal Runner for Reliance Stock BDA Platform")
    parser.add_argument("--pipeline-only", action="store_true", help="Run only the data & ML pipeline without launching the UI")
    parser.add_argument("--dashboard-only", action="store_true", help="Launch the Streamlit UI immediately using existing artifacts")
    args = parser.parse_args()

    print("*" * 75)
    print("   RELIANCE BDA STOCK PREDICTION PLATFORM — MASTER TERMINAL RUNNER")
    print("*" * 75)

    check_and_install_dependencies()

    if args.dashboard_only:
        launch_dashboard()
    elif args.pipeline_only:
        run_pipeline()
    else:
        # Default: Execute complete pipeline then launch dashboard
        run_pipeline()
        launch_dashboard()


if __name__ == "__main__":
    main()
