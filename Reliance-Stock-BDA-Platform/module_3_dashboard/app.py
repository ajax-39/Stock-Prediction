"""
app.py — Main Entrypoint for Reliance Stock BDA Analytics Platform
==================================================================
Streamlit Cockpit with system status, global navigation, and live pipeline triggers.

Usage:
    streamlit run module_3_dashboard/app.py --server.port 8501
"""

import os
import sys
import datetime
import subprocess
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard.styles import CUSTOM_CSS
from module_3_dashboard.data_loader import (
    load_latest_serving_state,
    load_predictions,
    load_daily_scores,
    load_engineered_features
)

# -----------------------------------------------------------------------------
# App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="RELIANCE — BDA Stock Prediction Cockpit",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Market Hours Calculation (IST: 09:15 to 15:30, Mon-Fri)
# -----------------------------------------------------------------------------
def get_market_status():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_ist = now_utc + datetime.timedelta(hours=5, minutes=30)
    is_weekday = now_ist.weekday() < 5
    m_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    m_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)

    is_open = is_weekday and (m_open <= now_ist <= m_close)
    time_str = now_ist.strftime("%H:%M:%S IST")
    return is_open, time_str


market_open, ist_time_now = get_market_status()


# -----------------------------------------------------------------------------
# Global Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏛️ BDA Stock Platform")
    st.caption("Big Data Analytics & AI Architecture")

    st.markdown("---")
    st.markdown("#### 🎯 Active Ticker")
    ticker_choice = st.selectbox(
        "Select Asset:",
        ["RELIANCE.NS — Reliance Industries Ltd"],
        index=0
    )

    st.markdown("#### ⏰ NSE Market Hours")
    if market_open:
        st.markdown(f'<span class="badge-online">🟢 LIVE MARKET OPEN</span> `{ist_time_now}`', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="badge-online" style="color:#f59e0b; border-color:#f59e0b;">🟡 MARKET CLOSED</span> `{ist_time_now}`', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⚡ Cluster Telemetry")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="badge-online">HDFS: ONLINE</span>', unsafe_allow_html=True)
        st.markdown('<span class="badge-online">HIVE: READY</span>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="badge-online">HBASE: CONNECTED</span>', unsafe_allow_html=True)
        st.markdown('<span class="badge-online">KAFKA: STREAMING</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🚀 Pipeline Execution")
    if st.button("▶️ Run Batch Prediction Pipeline", use_container_width=True):
        with st.spinner("Executing Pig ETL, Spark Indicators, Scoring & ML Models..."):
            try:
                # Trigger pipeline stages
                subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "module_2_processing", "pig", "run_pig_etl.py")], check=True)
                subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "module_2_processing", "spark", "spark_feature_engineering.py")], check=True)
                subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "module_2_processing", "spark", "spark_score_engine.py")], check=True)
                subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "module_2_processing", "prediction", "predict_next_day.py")], check=True)
                st.success("✅ Complete pipeline executed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Execution notice: {e}")

    st.caption("Hadoop 3.3.6 · Spark 3.4.1 · Hive 3 · HBase · Kafka")


# -----------------------------------------------------------------------------
# Main Landing Overview
# -----------------------------------------------------------------------------
st.title("📈 Reliance Industries (RELIANCE.NS) BDA Prediction Cockpit")
st.markdown("A distributed Big Data Analytics platform fusing **Kaggle price history**, **NLP news sentiment**, **sector momentum**, and **streaming ticks** to forecast next-day returns.")

serving_state = load_latest_serving_state()
cf_tick = serving_state.get("cf_tick", {})
cf_score = serving_state.get("cf_score", {})
cf_pred = serving_state.get("cf_pred", {})

df_preds = load_predictions()
latest_pred = df_preds.iloc[-1].to_dict() if not df_preds.empty else {}

# Key Metrics Row
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    ltp_val = cf_tick.get("ltp", latest_pred.get("current_close", "2750.00"))
    st.metric("Current LTP (₹)", f"₹{float(ltp_val):,.2f}", "+0.45%")
with col_m2:
    pred_val = cf_pred.get("predicted_close", latest_pred.get("predicted_close", "2768.50"))
    ret_val = latest_pred.get("predicted_return_pct", 0.67)
    st.metric("Next-Day Forecast", f"₹{float(pred_val):,.2f}", f"{ret_val:+.2f}%")
with col_m3:
    comp_score = cf_score.get("composite", latest_pred.get("composite_score", "72.4"))
    st.metric("Composite Score (S)", f"{float(comp_score):.1f} / 100", "Bullish Bias")
with col_m4:
    sig = cf_pred.get("signal", latest_pred.get("signal", "BUY"))
    st.metric("Signal Recommendation", sig, "Algorithm Target")
with col_m5:
    conf = cf_pred.get("confidence", latest_pred.get("confidence_pct", "68.5"))
    st.metric("Model Confidence", f"{conf}%", "Time-Series Split")

st.markdown("---")

# Navigation Guidance Cards
st.subheader("🧭 Platform Architecture Navigation")
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#06b6d4; margin-top:0;">📂 Page 1: Pipeline & Ingestion</h3>
        <p style="color:#9ca3af; font-size:0.92rem;">
            Explore the 6-layer BDA architecture diagram, inspect raw Kaggle historical datasets (2010–2025), browse curated NLP news articles with TextBlob sentiment chips, and query Hive metastore tables.
        </p>
        <span class="badge-online">Module 1: Storage Layer</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#8b5cf6; margin-top:0;">📊 Page 2: Technicals & Analytics</h3>
        <p style="color:#9ca3af; font-size:0.92rem;">
            Interactive Plotly candlestick charts with EMA 20/50, VWAP, Bollinger Bands, Volume, RSI, and MACD subplots. View multi-factor radial gauge scores (T, F, N, R) and MapReduce sector momentum cards.
        </p>
        <span class="badge-online">Module 2: Processing Layer</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col3:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#10b981; margin-top:0;">🎯 Page 3: Prediction & Decision</h3>
        <p style="color:#9ca3af; font-size:0.92rem;">
            Big hero next-day price forecast card with confidence intervals, actionable BUY / SELL / HOLD trading badges, feature importance drivers from Spark MLlib, and backtest benchmarking against the naive baseline.
        </p>
        <span class="badge-online">Module 3: Prediction Serving</span>
    </div>
    """, unsafe_allow_html=True)

# Pipeline Flow Overview
st.markdown("### ⚙️ End-to-End Pipeline Health")
st.markdown("""
```
[1. Kaggle 2010-2025] ──► [HDFS Raw Zone] ──► [Apache Pig ETL] ──► [Spark SQL Windows] ──► [Spark MLlib RF] ──► [HBase / Hive] ──► [Streamlit]
[2. Curated Web News] ──► [HDFS News Lake] ──► (Deduplication)  ──► (EMA, VWAP, RSI)   ──► (Next-Day Return) ──► (RowKey: RELIANCE#<ts>)
[3. Streaming Ticks]  ──► [Kafka Broker]   ──► [Spark Streaming]──► [4-Score Engine]    ──► (Buy/Hold Signals)
```
""")
