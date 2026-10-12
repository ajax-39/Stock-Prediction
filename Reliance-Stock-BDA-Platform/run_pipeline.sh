#!/bin/bash
# ============================================================================
# run_pipeline.sh — Linux / Docker / WSL Runner for Reliance BDA Platform
# ============================================================================
set -e

echo "=== Starting Reliance BDA Pipeline Orchestration ==="
python3 orchestrator.py
echo "=== Pipeline completed successfully. ==="
