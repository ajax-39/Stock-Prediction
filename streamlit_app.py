"""
streamlit_app.py — Root Entrypoint for Streamlit Community Cloud
================================================================
Entrypoint proxy that configures Python paths and delegates execution to the
StockPulse BDA Presentation Cockpit in Reliance-Stock-BDA-Platform/module_3_dashboard/app.py.
"""

import os
import sys
import runpy

# Ensure repository root and platform directory are on sys.path
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
PLATFORM_ROOT = os.path.join(REPO_ROOT, "Reliance-Stock-BDA-Platform")

for path in (PLATFORM_ROOT, REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

# Target dashboard entrypoint
APP_PATH = os.path.join(PLATFORM_ROOT, "module_3_dashboard", "app.py")

if not os.path.exists(APP_PATH):
    raise FileNotFoundError(f"Dashboard entrypoint not found at {APP_PATH}")

# Execute the application in the __main__ namespace
runpy.run_path(APP_PATH, run_name="__main__")
