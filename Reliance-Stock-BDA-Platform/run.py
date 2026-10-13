"""
run.py — Single Master Terminal Launcher for Reliance BDA Platform
==================================================================
Runs the complete Big Data Analytics project with a single command from your terminal:
    1. Verifies Python dependencies.
    2. Executes full BDA data pipeline (Kaggle Ingest -> Pig ETL -> MapReduce -> Spark -> MLlib).
    3. Generates next-day stock price prediction and trading signals for RELIANCE.
    4. Automatically launches the interactive Streamlit Cockpit on http://localhost:8501.

Usage:
    python run.py
    python run.py --pipeline-only     (runs data & ML pipeline without launching UI)
    python run.py --dashboard-only    (launches UI immediately using cached artifacts)
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

# Resolve project root whether executed from workspace or from platform directory
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
    print("  🚀 EXECUTING END-TO-END BDA PIPELINE (KAGGLE + PIG + MR + SPARK + MLLIB)")
    print("=" * 75)
    t0 = time.time()
    res = subprocess.run([sys.executable, orchestrator_script, "--local-standalone"], cwd=PROJECT_ROOT)
    elapsed = time.time() - t0
    if res.returncode != 0:
        print(f"\n❌ Pipeline execution encountered an error (exit code: {res.returncode})")
        sys.exit(res.returncode)
    print(f"\n✅ Pipeline completed successfully in {elapsed:.2f}s!")


def launch_dashboard():
    """Launches the Streamlit presentation dashboard and opens browser."""
    app_script = os.path.join(PROJECT_ROOT, "module_3_dashboard", "app.py")
    port = 8501
    url = f"http://localhost:{port}"

    print("\n" + "=" * 75)
    print(f"  🌐 LAUNCHING STREAMLIT PRESENTATION COCKPIT ON {url}")
    print("=" * 75)
    print(f"  - App entrypoint: {app_script}")
    print(f"  - URL: {url}")
    print("  - Press CTRL+C in this terminal window to stop the server at any time.\n")

    # Automatically open default browser after brief delay
    def open_browser():
        time.sleep(2.0)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch Streamlit server in foreground so terminal displays logs
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_script,
        f"--server.port={port}",
        "--server.headless=false"
    ]
    try:
        subprocess.run(cmd, cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        print("\n  🛑 Dashboard server stopped by user.")


def main():
    parser = argparse.ArgumentParser(description="Master Terminal Runner for Reliance Stock BDA Platform")
    parser.add_argument("--pipeline-only", action="store_true", help="Run only the data & ML pipeline without launching the UI")
    parser.add_argument("--dashboard-only", action="store_true", help="Launch the Streamlit UI immediately using existing artifacts")
    args = parser.parse_args()

    print("*" * 75)
    print("   RELIANCE BDA STOCK PREDICTION PLATFORM — ALL-IN-ONE TERMINAL RUNNER")
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
