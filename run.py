"""
run.py — Workspace Root Master Launcher
=======================================
Redirects to Reliance-Stock-BDA-Platform/run.py so you can run the entire
project directly from the root workspace directory.

Usage:
    python run.py
"""

import os
import sys
import subprocess

TARGET = os.path.join(os.path.dirname(__file__), "Reliance-Stock-BDA-Platform", "run.py")

if __name__ == "__main__":
    if not os.path.exists(TARGET):
        print(f"Error: Target runner not found at {TARGET}")
        sys.exit(1)
    # Forward all command line arguments
    sys.exit(subprocess.call([sys.executable, TARGET, *sys.argv[1:]]))
