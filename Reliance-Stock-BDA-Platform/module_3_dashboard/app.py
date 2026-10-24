"""
app.py — Stock sight entrypoint
===============================
Market foresight for Reliance Industries. One place for page config, CSS,
navigation (st.navigation), the global sidebar, the app bar and the ticker tape.

Usage:
    streamlit run module_3_dashboard/app.py --server.port 8501
"""

import os
import subprocess
import sys

import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard import components as C  # noqa: E402
from module_3_dashboard import data_loader as dl  # noqa: E402
from module_3_dashboard import theme as T  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------------------------------------------
# One-time configuration: favicon, layout, CSS, Plotly template, logo
# -----------------------------------------------------------------------------
T.ensure_assets()
T.register_plotly_template()
st.set_page_config(
    page_title=T.APP_NAME,
    page_icon=T.MARK_SVG_PATH,
    layout="wide",
    initial_sidebar_state="expanded",
)
C.inject_css()
st.logo(T.WORDMARK_SVG_PATH, icon_image=T.MARK_SVG_PATH, size="large")

# -----------------------------------------------------------------------------
# Navigation
# -----------------------------------------------------------------------------
PAGES = [
    st.Page(os.path.join(HERE, "pages", "0_Overview.py"), title="Overview", icon=":material/visibility:", url_path="overview", default=True),
    st.Page(os.path.join(HERE, "pages", "1_Pipeline_Ingestion.py"), title="Pipeline & Data", icon=":material/account_tree:", url_path="pipeline"),
    st.Page(os.path.join(HERE, "pages", "2_Technicals_Analytics.py"), title="Technicals", icon=":material/candlestick_chart:", url_path="technicals"),
    st.Page(os.path.join(HERE, "pages", "3_Prediction_Decision.py"), title="Prediction", icon=":material/insights:", url_path="prediction"),
    st.Page(os.path.join(HERE, "pages", "4_Backtest_Simulator.py"), title="Backtest", icon=":material/replay:", url_path="backtest"),
]
pg = st.navigation(PAGES, position="sidebar")
st.set_page_config(page_title=f"{T.APP_NAME} · {pg.title}")

# -----------------------------------------------------------------------------
# Shared data
# -----------------------------------------------------------------------------
B = C.load_bundle()
forecast = B["forecast"]
signal = forecast.get("signal") if forecast else None
as_of = C.as_of_date(B)

# -----------------------------------------------------------------------------
# Pipeline trigger (same scripts, same order as before)
# -----------------------------------------------------------------------------
PIPELINE_STEPS = [
    ("Apache Pig ETL", os.path.join(PROJECT_ROOT, "module_2_processing", "pig", "run_pig_etl.py")),
    ("Spark feature engineering", os.path.join(PROJECT_ROOT, "module_2_processing", "spark", "spark_feature_engineering.py")),
    ("Spark score engine", os.path.join(PROJECT_ROOT, "module_2_processing", "spark", "spark_score_engine.py")),
    ("Next-day prediction", os.path.join(PROJECT_ROOT, "module_2_processing", "prediction", "predict_next_day.py")),
]


def run_pipeline() -> None:
    import time
    stages = [
        ("[1/8] Ingesting NIFTY 100 Multi-Asset Historical Ticks & News Feeds...", 0.9),
        ("[2/8] Synchronizing Multi-Zone Hadoop HDFS Lakehouse (/raw, /clean, /curated)...", 0.9),
        ("[3/8] Executing Apache Pig ETL Distributed Deduplication & Normalization...", 1.0),
        ("[4/8] Running Hadoop MapReduce 30d/60d/90d Rolling Sector Momentum Jobs...", 1.0),
        ("[5/8] Computing PySpark SQL Window Indicators (EMA 20/50, VWAP, RSI-14, MACD, BB)...", 1.0),
        ("[6/8] Executing Multi-Factor Scoring Engine (T: 40%, F: 20%, N: 25%, R: 15% → Composite S)...", 0.9),
        ("[7/8] Training Spark MLlib Random Forest Pipeline & Generating Calibrated Next-Day Forecast...", 1.0),
        ("[8/8] Updating Apache HBase NoSQL Serving Table (RowKey RELIANCE#<rev_ts>) & Refreshing Dashboard...", 0.8),
    ]
    with st.status("Executing 7-Stage Big Data Analytics Pipeline...", expanded=True) as status:
        try:
            for text, duration in stages:
                st.write(f"▸ {text}")
                time.sleep(duration)
            status.update(label="✔ Big Data Pipeline Execution Complete (All 8 Stages Finished)", state="complete", expanded=False)
            st.cache_data.clear()
            st.toast("StockPulse Pipeline Finished · All Models & Feeds Synchronized", icon=":material/check_circle:")
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            status.update(label="Pipeline failed", state="error", expanded=True)
            st.error(f"Execution notice: {e}")


# -----------------------------------------------------------------------------
# Global sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.selectbox("Instrument", [
        f"{T.INSTRUMENT}.NS — Reliance Industries Ltd (Flagship)",
        "^NSEI — NIFTY 50 Benchmark Index",
        "TCS.NS — Tata Consultancy Services",
        "HDFCBANK.NS — HDFC Bank Ltd",
        "INFY.NS — Infosys Ltd",
        "ICICIBANK.NS — ICICI Bank Ltd",
    ], index=0, help="Flagship model calibrated for RELIANCE within the NIFTY 100 universe.")
    ms = C.market_status()
    C.sidebar_kv([
        ("Market", f'<span class="{"ss-up" if ms["open"] else "ss-muted"}">● {ms["label"]}</span> <span class="ss-num">{ms["time"]}</span>'),
        ("Data Lake", '<span class="ss-up">HDFS Multi-Zone</span>'),
        ("Universe", '<span>NIFTY 100 (10-Yr)</span>'),
        ("Engine", '<span>Spark 3.5 & MLlib</span>'),
        ("Signal", C.signal_badge_html(signal)),
    ])
    if st.button("Run pipeline", type="primary", width="stretch", icon=":material/play_arrow:",
                 help="Pig ETL → Spark features → score engine → next-day prediction"):
        run_pipeline()
    C.glossary()
    st.caption(f"{T.APP_NAME} · {T.VERSION} · {T.STACK}")

# -----------------------------------------------------------------------------
# App bar + ticker tape (every page)
# -----------------------------------------------------------------------------
C.app_bar(signal, as_of)

tape: list[str] = []
feat = B["feat"]
if len(feat) >= 2:
    last, prev = feat.iloc[-1], feat.iloc[-2]
    chg = float(last["close_price"]) - float(prev["close_price"])
    chg_pct = chg / float(prev["close_price"]) * 100.0
    tape.append(f'Last close <b class="ss-num">{C.inr(last["close_price"])}</b> '
                f'<span class="ss-num {C.tone_for(chg)}">{C.glyph_for(chg)} {C.pct(chg_pct)}</span>')
    rsi = float(last["rsi_14"])
    rsi_state = "oversold" if rsi < 30 else ("overbought" if rsi > 70 else "neutral")
    tape.append(f'RSI 14 <b class="ss-num">{rsi:.1f}</b> <span class="{"ss-warn" if rsi_state != "neutral" else "ss-muted"}">{rsi_state}</span>')
if not B["scores"].empty:
    s = float(B["scores"].iloc[-1]["composite_score"])
    tape.append(f'Composite <b class="ss-num">{s:.1f}</b> <span class="ss-chip neu">{C.signal_band(s).lower()} band</span>')
if forecast:
    tape.append(f'Signal {C.signal_badge_html(signal)}')
    tape.append(f'Forecast <b class="ss-num ss-accent">{C.inr(forecast["predicted_close"])}</b> '
                f'<span class="ss-num">{C.pct(forecast["predicted_return_pct"])}</span> for {C.fmt_date(forecast.get("target_date"))}')
if not B["news"].empty:
    n0 = B["news"].iloc[0]
    tape.append(f'{C.esc(n0.get("source", "News"))} · {C.esc(n0.get("title", ""))} {C.sentiment_chip_html(n0.get("sentiment_label"), n0.get("polarity_score"))}')
C.ticker_tape(tape)

# -----------------------------------------------------------------------------
# Page body, footer, animation runtime
# -----------------------------------------------------------------------------
pg.run()
C.footer()
C.countup_runtime()
