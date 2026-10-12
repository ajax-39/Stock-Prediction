"""
1_Pipeline_Ingestion.py — Data Ingestion & BDA Pipeline Architecture Inspector
=============================================================================
Visualizes data sources, HDFS raw storage, Hive schema, and the multi-stage BDA pipeline.
"""

import os
import sys
import pandas as pd
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard.styles import CUSTOM_CSS
from module_3_dashboard.data_loader import (
    load_raw_prices,
    load_curated_news,
    load_market_sentiment
)

st.set_page_config(page_title="Pipeline & Ingestion — RELIANCE BDA", page_icon="📂", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("📂 Module 1: Ingestion & Distributed Storage Architecture")
st.markdown("Inspection console for Big Data ingestion sources, HDFS Lake structure, and Hive Warehouse tables.")

# -----------------------------------------------------------------------------
# Section 1: Visual Interactive BDA Architecture Pipeline
# -----------------------------------------------------------------------------
st.subheader("🏗️ Distributed Big Data Pipeline Flow")
st.markdown("""
<div class="glass-card">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div style="background:#1f2937; padding:12px 16px; border-radius:10px; border:1px solid #374151; text-align:center; flex:1; min-width:140px;">
            <div style="font-size:0.75rem; color:#9ca3af; font-weight:600;">SOURCE FEEDS</div>
            <div style="font-weight:700; color:#38bdf8; margin:4px 0;">Kaggle + RSS + Ticks</div>
            <div style="font-size:0.7rem; color:#6b7280;">2010-2025 OHLCV, TextBlob</div>
        </div>
        <div style="color:#6b7280; font-size:1.2rem;">➔</div>
        <div style="background:#1f2937; padding:12px 16px; border-radius:10px; border:1px solid #374151; text-align:center; flex:1; min-width:140px;">
            <div style="font-size:0.75rem; color:#9ca3af; font-weight:600;">HDFS DATA LAKE</div>
            <div style="font-weight:700; color:#34d399; margin:4px 0;">/bda/lake/raw/*</div>
            <div style="font-size:0.7rem; color:#6b7280;">HDFS NameNode :9000</div>
        </div>
        <div style="color:#6b7280; font-size:1.2rem;">➔</div>
        <div style="background:#1f2937; padding:12px 16px; border-radius:10px; border:1px solid #374151; text-align:center; flex:1; min-width:140px;">
            <div style="font-size:0.75rem; color:#9ca3af; font-weight:600;">BATCH ETL & MR</div>
            <div style="font-weight:700; color:#fbbf24; margin:4px 0;">Apache Pig & MapReduce</div>
            <div style="font-size:0.7rem; color:#6b7280;">Deduplication & Momentum</div>
        </div>
        <div style="color:#6b7280; font-size:1.2rem;">➔</div>
        <div style="background:#1f2937; padding:12px 16px; border-radius:10px; border:1px solid #374151; text-align:center; flex:1; min-width:140px;">
            <div style="font-size:0.75rem; color:#9ca3af; font-weight:600;">ANALYTICS & ML</div>
            <div style="font-weight:700; color:#a78bfa; margin:4px 0;">Spark SQL & MLlib</div>
            <div style="font-size:0.7rem; color:#6b7280;">4 Scores (T,F,N,R) & GBT</div>
        </div>
        <div style="color:#6b7280; font-size:1.2rem;">➔</div>
        <div style="background:#1f2937; padding:12px 16px; border-radius:10px; border:1px solid #374151; text-align:center; flex:1; min-width:140px;">
            <div style="font-size:0.75rem; color:#9ca3af; font-weight:600;">FAST SERVING</div>
            <div style="font-weight:700; color:#f43f5e; margin:4px 0;">HBase + Hive</div>
            <div style="font-size:0.7rem; color:#6b7280;">RowKey: RELIANCE#rev_ts</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 2: Data Source 1 — Kaggle Historical OHLCV
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📊 Data Source 1: Kaggle Historical OHLCV (2010–2025)")

df_prices = load_raw_prices()
if not df_prices.empty:
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Total Trading Sessions", f"{len(df_prices):,} Days")
    with m_col2:
        st.metric("Timeline Range", f"{df_prices['Date'].min()} to {df_prices['Date'].max()}")
    with m_col3:
        st.metric("Highest Historical Close", f"₹{df_prices['Close'].max():,.2f}")
    with m_col4:
        st.metric("Average Daily Volume", f"{int(df_prices['Volume'].mean()):,} Shares")

    with st.expander("🔍 Explore Raw Kaggle Historical Data Table", expanded=False):
        num_rows = st.slider("Rows to display:", 5, 50, 10)
        st.dataframe(df_prices.tail(num_rows), use_container_width=True)
else:
    st.warning("Raw prices dataset not found. Run module_1_storage/ingestion/kaggle_ingest.py first.")

# -----------------------------------------------------------------------------
# Section 3: Data Source 2 — Curated News & NLP Sentiment Feed
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📰 Data Source 2: Curated News & TextBlob Sentiment")

df_news = load_curated_news()
if not df_news.empty:
    news_cols = st.columns(len(df_news))
    for idx, row in df_news.iterrows():
        with news_cols[idx % len(news_cols)]:
            pol = float(row.get("polarity_score", 0.0))
            chip_cls = "sentiment-chip-pos" if pol >= 0 else "sentiment-chip-neg"
            sign_str = f"+{pol:.2f}" if pol >= 0 else f"{pol:.2f}"

            st.markdown(f"""
            <div class="glass-card" style="height:260px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:0.75rem; color:#9ca3af; font-weight:600;">{row.get('source', 'News')}</span>
                        <span class="{chip_cls}">{row.get('sentiment_label', 'NEUTRAL')} ({sign_str})</span>
                    </div>
                    <div style="font-weight:600; font-size:0.88rem; color:#f3f4f6; line-height:1.3; margin-bottom:6px;">
                        {row.get('title', '')}
                    </div>
                    <div style="font-size:0.75rem; color:#9ca3af; line-height:1.4;">
                        {row.get('summary', '')[:120]}...
                    </div>
                </div>
                <div style="font-size:0.7rem; color:#6b7280; margin-top:6px;">
                    📅 {row.get('trade_date', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Curated news feed empty. Run module_1_storage/ingestion/news_curated_feed.py.")

# -----------------------------------------------------------------------------
# Section 4: Data Source 3 — Sector & Macro Sentiment
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🌐 Data Source 3: Sector & Macro Environment (Oil & Gas & NIFTY 50)")

df_sent = load_market_sentiment()
if not df_sent.empty:
    latest_macro = df_sent.iloc[-1]
    sec_col1, sec_col2, sec_col3, sec_col4 = st.columns(4)
    with sec_col1:
        st.metric("Sector Benchmark", latest_macro.get("sector", "Energy"), "Oil & Gas / O2C")
    with sec_col2:
        st.metric("Sector P/E Ratio", f"{latest_macro.get('sector_pe_ratio', 24.8):.1f}x", "Historical Mean")
    with sec_col3:
        st.metric("NIFTY 50 Sentiment", f"{latest_macro.get('nifty50_sentiment_score', 68.0):.1f} / 100", latest_macro.get('nifty50_sentiment_label', 'BULLISH'))
    with sec_col4:
        st.metric("Brent Crude Price", f"${latest_macro.get('brent_crude_usd', 78.5):.2f}/bbl", "Stable Input Cost")
else:
    st.info("Market sentiment data not available.")

# -----------------------------------------------------------------------------
# Section 5: HDFS Data Lake & Hive Metastore Inspector
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("🗄️ HDFS Data Lake & Hive Warehouse Metastore Inspector")

lake_tab1, lake_tab2 = st.tabs(["HDFS 3-Zone Hierarchy", "Hive Warehouse Schemas"])

with lake_tab1:
    st.markdown("""
    | Zone | HDFS Target Path | Format | Status | Purpose |
    | :--- | :--- | :---: | :---: | :--- |
    | **Raw Prices** | `/bda/lake/raw/prices/reliance_prices.csv` | CSV | ✅ MOUNTED | Immutable Kaggle 2010–2025 raw historical prices |
    | **Raw News** | `/bda/lake/raw/news/reliance_news.csv` | CSV | ✅ MOUNTED | Financial headlines with TextBlob sentiment tags |
    | **Raw Macro** | `/bda/lake/raw/sentiment/market_sentiment.csv` | CSV | ✅ MOUNTED | NIFTY 50 and Energy sector index parameters |
    | **Clean Zone** | `/bda/lake/clean/reliance_daily_joined/` | CSV/Parquet | ✅ SYNCHRONIZED | Output of Apache Pig normalization and joining |
    | **Curated Zone**| `/bda/lake/curated/reliance_features/` | ORC | ✅ READY | Windowed indicators (EMA, VWAP, RSI, MACD, BB) |
    | **Model Store**| `/bda/models/reliance_mllib_best/` | Spark ML | ✅ TRAINED | Saved Spark MLlib Random Forest model weights |
    """)

with lake_tab2:
    st.markdown("""
    ```sql
    -- Active Hive Tables in 'reliance_bda_db'
    CREATE EXTERNAL TABLE raw_stock_prices (trade_date STRING, open_price DOUBLE, high_price DOUBLE, low_price DOUBLE, close_price DOUBLE, volume BIGINT, ticker STRING)
    LOCATION '/bda/lake/raw/prices';

    CREATE TABLE reliance_features (trade_date STRING, close_price DOUBLE, ema_20 DOUBLE, ema_50 DOUBLE, vwap DOUBLE, rsi_14 DOUBLE, macd DOUBLE, bb_pos DOUBLE)
    PARTITIONED BY (year STRING, month STRING) STORED AS ORC;

    CREATE TABLE reliance_daily_scores (trade_date STRING, technical_score DOUBLE, fundamental_score DOUBLE, news_score DOUBLE, realtime_score DOUBLE, composite_score DOUBLE)
    STORED AS ORC;

    CREATE TABLE reliance_predictions (trade_date STRING, predicted_close DOUBLE, direction STRING, signal STRING, confidence DOUBLE)
    STORED AS ORC;
    ```
    """)
