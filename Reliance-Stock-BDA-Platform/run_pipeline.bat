@echo off
REM ============================================================================
REM run_pipeline.bat — Windows One-Click Runner for Reliance BDA Platform
REM ============================================================================
echo Starting Reliance BDA Pipeline Orchestration on Windows...
python orchestrator.py
echo Pipeline completed. To launch the dashboard run:
echo streamlit run module_3_dashboard\app.py
pause
