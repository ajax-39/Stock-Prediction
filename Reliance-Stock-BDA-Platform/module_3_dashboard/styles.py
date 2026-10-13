"""
styles.py — Backward-compatible shim.
=====================================
The design system now lives in theme.py (tokens, CSS, Plotly template).
This module only re-exports CUSTOM_CSS so older imports keep working.
"""

from module_3_dashboard.theme import CUSTOM_CSS  # noqa: F401
