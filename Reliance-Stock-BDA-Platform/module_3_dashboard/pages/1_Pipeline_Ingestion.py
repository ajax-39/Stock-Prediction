"""
1_Pipeline_Ingestion.py — Pipeline & Data
=========================================
Where every number comes from: the sources, the storage zones and the stages
that transform them. Statuses, row counts and timestamps are read from disk.
"""

import os
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard import components as C  # noqa: E402
from module_3_dashboard import data_loader as dl  # noqa: E402

B = C.load_bundle()
prices, news, macro = B["prices"], B["news"], B["macro"]

C.page_title("Pipeline & Data", "Sources → HDFS lake → Pig / MapReduce → Spark SQL & scoring → MLlib → HBase / Hive → Stock sight. "
             "Every status below is read from the staged files, not assumed.")

# -----------------------------------------------------------------------------
# Architecture flow (kept from the original page, restyled)
# -----------------------------------------------------------------------------
C.flow_diagram([
    ("Source feeds", "Kaggle · news · ticks", "2010–2025 OHLCV, TextBlob NLP, broker stub"),
    ("HDFS data lake", "/bda/lake/raw/*", "NameNode :9000 · 3 zones"),
    ("Batch ETL & MR", "Apache Pig · MapReduce", "Dedup, joins, 30/60/90d momentum"),
    ("Analytics & ML", "Spark SQL · MLlib", "EMA, VWAP, RSI, MACD, BB · T/F/N/R → S"),
    ("Fast serving", "HBase · Hive", "RowKey RELIANCE#rev_ts · ORC tables"),
])

# -----------------------------------------------------------------------------
# Stage status table
# -----------------------------------------------------------------------------
C.section("Stage status", "status, rows, date coverage and last-modified time from the files on disk")
stages = dl.pipeline_stages()
rows = []
for s in stages:
    if not s["exists"]:
        status = "● missing"
    elif s.get("error"):
        status = "● unreadable"
    else:
        age_h = (pd.Timestamp.now() - pd.Timestamp(s["mtime"])).total_seconds() / 3600
        status = "● fresh" if age_h < 24 else "● stale (>24 h)"
    rows.append({
        "Stage": s["stage"], "Engine": s["engine"], "File": s["name"], "Status": status,
        "Rows": s["rows"], "From": s["date_min"], "To": s["date_max"],
        "Last modified": s["mtime"].strftime("%Y-%m-%d %H:%M") if s["mtime"] else None,
        "Size (KB)": round(s["size_bytes"] / 1024, 1) if s["size_bytes"] else None,
    })
df_stages = pd.DataFrame(rows)
C.table(df_stages, "pipeline_stages", column_config={
    "Rows": st.column_config.NumberColumn("Rows", format="localized"),
    "Size (KB)": st.column_config.NumberColumn("Size (KB)", format="%.1f"),
    "Status": st.column_config.TextColumn("Status", help="fresh = modified in the last 24 h"),
})

# -----------------------------------------------------------------------------
# Data quality
# -----------------------------------------------------------------------------
C.section("Data quality", "missing values, date gaps and the news → price join")
q = dl.data_quality_report()
files_ok = [f for f in q["files"] if f.get("exists") and "rows" in f]
missing_total = int(sum(f["missing"] for f in files_ok))
dup_total = int(sum((f.get("duplicate_dates") or 0) for f in files_ok))
nm, gaps = q.get("news_match"), q.get("date_gaps")
c1, c2, c3, c4 = st.columns(4)
with c1:
    C.metric("Missing values", float(missing_total), fmt="num", dec=0, key="dq_missing",
             delta_text=f"across {len(files_ok)} files", sub="cells with NaN in any staged CSV")
with c2:
    C.metric("Duplicate dates", float(dup_total), fmt="num", dec=0, key="dq_dup", sub="repeated trade_date keys")
with c3:
    if gaps:
        C.metric("Date gaps > 5 days", float(gaps["count"]), fmt="num", dec=0, key="dq_gaps",
                 sub=f"largest gap {gaps['max_days']} calendar days" + (" · weekends only" if gaps["weekend_only"] else ""))
    else:
        C.metric("Date gaps", "—", sub="no price history")
with c4:
    if nm and nm["total"]:
        C.metric("News → price join", f"{nm['matched']} / {nm['total']}", delta=None,
                 delta_text=f"{nm['rate_pct']}% matched", sub="headline dates that exist as trading days")
    else:
        C.metric("News → price join", "—", sub="no news rows")
if nm and nm["total"] and nm["matched"] == 0:
    C.note(f"<b>0 of {nm['total']} headlines join to a trading day.</b> News is dated {C.fmt_date(nm['news_min'])} – "
           f"{C.fmt_date(nm['news_max'])}; the price history ends {C.fmt_date(nm['price_max'])}. The Pig join therefore leaves "
           f"<code>news_polarity = 0</code> on every row ({nm['feature_days_with_news'] or 0} feature days carry news) and the news score N "
           f"is flat at 50. Fix: refresh the Kaggle download or back-date the curated feed.", kind="warn")
with st.expander("Per-file detail"):
    dq_rows = [{"File": f["name"], "Exists": f.get("exists", False), "Rows": f.get("rows"), "Columns": f.get("cols"),
                "Missing cells": f.get("missing"), "Missing %": f.get("missing_pct"), "Duplicate dates": f.get("duplicate_dates"),
                "Error": f.get("error")} for f in q["files"]]
    C.table(pd.DataFrame(dq_rows), "data_quality", column_config={
        "Rows": st.column_config.NumberColumn(format="localized"), "Missing %": st.column_config.NumberColumn(format="%.3f%%")})
    if gaps and gaps["examples"]:
        st.caption("Largest gaps: " + " · ".join(f"{a} → {b} ({d} d)" for a, b, d in gaps["examples"]))

# -----------------------------------------------------------------------------
# Source 1 · Kaggle historical OHLCV
# -----------------------------------------------------------------------------
src = B["source"]
C.section("Source 1 · Kaggle historical OHLCV", f'{C.freshness_tag(dl.RAW_PRICES)} · detected as <b>{C.esc(src["source"])}</b>')
if prices.empty:
    C.empty_state("Raw prices dataset not found", "Run module_1_storage/ingestion/kaggle_ingest.py first.", dl.RAW_PRICES)
else:
    if src["source"] != "Kaggle":
        C.note(f"<b>{C.esc(src['source'])}</b>: {C.esc(src['reason'])}. Prices are a seeded random walk, not Reliance's real history, "
               f"so levels like {C.inr(prices['Close'].iloc[-1])} are not comparable to the NSE quote.", kind="warn")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        C.metric("Trading sessions", float(len(prices)), fmt="num", dec=0, key="p_sessions")
    with m2:
        C.metric("Timeline", f"{C.fmt_date(prices['Date'].min())} – {C.fmt_date(prices['Date'].max())}",
                 sub=f"{(pd.to_datetime(prices['Date'].max()) - pd.to_datetime(prices['Date'].min())).days // 365} years")
    with m3:
        hi = prices.loc[prices["Close"].idxmax()]
        C.metric("Highest close", float(hi["Close"]), key="p_hi", sub=f"on {C.fmt_date(hi['Date'])}")
    with m4:
        C.metric("Average daily volume", C.compact_in(prices["Volume"].mean()), sub=f"median {C.compact_in(prices['Volume'].median())}")
    with st.expander("Explore the raw price table"):
        f1, f2 = st.columns([2, 1])
        with f1:
            filtered = C.date_range_filter(prices, "Date", key="raw_prices_range", default_days=None, label="Date range")
        with f2:
            n_rows = st.slider("Rows to display", 5, 50, 10, key="raw_rows")
        st.caption(f"{len(filtered):,} rows in range · showing the latest {min(n_rows, len(filtered))}")
        C.table(filtered.tail(n_rows), "raw_prices_preview", column_config={
            c: st.column_config.NumberColumn(c, format="₹%.2f") for c in ("Open", "High", "Low", "Close")} | {
            "Volume": st.column_config.NumberColumn("Volume", format="localized")}, download=False)
        C.csv_download(filtered, "raw_prices_filtered", key="dl_raw_prices_filtered")

# -----------------------------------------------------------------------------
# Source 2 · News & sentiment feed
# -----------------------------------------------------------------------------
C.section("Source 2 · News & TextBlob sentiment", C.freshness_tag(dl.RAW_NEWS))
if news.empty:
    C.empty_state("Curated news feed empty", "Run module_1_storage/ingestion/news_curated_feed.py.", dl.RAW_NEWS)
else:
    if nm and nm["total"] and nm["matched"] == 0:
        C.note(f"These headlines ({C.fmt_date(nm['news_min'])} – {C.fmt_date(nm['news_max'])}) fall outside the price history "
               f"(ends {C.fmt_date(nm['price_max'])}), so none of them reach the features or the news score.", kind="warn")
    C.news_cards(news.sort_values("trade_date", ascending=False) if "trade_date" in news.columns else news)
    with st.expander("News table"):
        C.table(news, "news_feed", column_config={"link": st.column_config.LinkColumn("link"),
                                                  "polarity_score": st.column_config.NumberColumn(format="%+.2f"),
                                                  "subjectivity_score": st.column_config.NumberColumn(format="%.2f")})

# -----------------------------------------------------------------------------
# Source 3 · Sector & macro environment
# -----------------------------------------------------------------------------
C.section("Source 3 · Sector & macro environment", C.freshness_tag(dl.RAW_SENTIMENT))
if macro.empty:
    C.empty_state("Market sentiment data not available", "Run module_1_storage/ingestion/sector_nifty_sentiment.py.", dl.RAW_SENTIMENT)
else:
    lm = macro.iloc[-1]
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    with s1:
        C.metric("Sector", str(lm.get("sector", "—")), sub=f"as of {C.fmt_date(lm.get('trade_date'))}")
    with s2:
        C.metric("Sector P/E", float(lm["sector_pe_ratio"]), fmt="num", dec=1, key="m_pe", delta_text="ratio",
                 spark=macro["sector_pe_ratio"].tail(30).tolist())
    with s3:
        C.metric("NIFTY 50 sentiment", float(lm["nifty50_sentiment_score"]), fmt="num", dec=1, key="m_nifty",
                 delta_text=str(lm.get("nifty50_sentiment_label", "")).lower(), spark=macro["nifty50_sentiment_score"].tail(30).tolist())
    with s4:
        C.metric("Brent crude", float(lm["brent_crude_usd"]), fmt="num", dec=2, key="m_brent", delta_text="USD / bbl",
                 spark=macro["brent_crude_usd"].tail(30).tolist())
    with s5:
        C.metric("India VIX", float(lm["india_vix"]), fmt="num", dec=1, key="m_vix", spark=macro["india_vix"].tail(30).tolist())
    with s6:
        C.metric("FII + DII net flow", float(lm["fii_dii_net_flow_cr"]), fmt="num", dec=0, key="m_flow", delta_text="₹ crore",
                 spark=macro["fii_dii_net_flow_cr"].tail(30).tolist())
    with st.expander("Macro table"):
        C.table(macro, "market_sentiment")

# -----------------------------------------------------------------------------
# HDFS lake & Hive metastore inspectors
# -----------------------------------------------------------------------------
C.section("HDFS data lake & Hive warehouse", "zone layout, table DDL and the locally staged mirror of each path")
tab_hdfs, tab_hive, tab_raw = st.tabs(["HDFS 3-zone hierarchy", "Hive warehouse schemas", "Staged previews"])

with tab_hdfs:
    zones = [
        ("Raw prices", "/bda/lake/raw/prices/reliance_prices.csv", "CSV", dl.RAW_PRICES, "Immutable Kaggle 2010–2025 history"),
        ("Raw news", "/bda/lake/raw/news/reliance_news.csv", "CSV", dl.RAW_NEWS, "Headlines with TextBlob sentiment"),
        ("Raw macro", "/bda/lake/raw/sentiment/market_sentiment.csv", "CSV", dl.RAW_SENTIMENT, "NIFTY 50 and energy-sector parameters"),
        ("Clean zone", "/bda/lake/clean/reliance_daily_joined/", "CSV / Parquet", dl.CLEAN_JOINED, "Pig normalisation and price–news join"),
        ("Curated zone", "/bda/lake/curated/reliance_features/", "ORC", dl.CURATED_FEATURES, "Windowed indicators (EMA, VWAP, RSI, MACD, BB)"),
        ("Model store", "/bda/models/reliance_mllib_best/", "Spark ML", dl.MODEL_METRICS, "Model metrics (weights are not staged locally)"),
    ]
    zrows = []
    for zone, path, fmt, local, purpose in zones:
        fi = dl.file_info(local)
        zrows.append({"Zone": zone, "HDFS path": path, "Format": fmt,
                      "Local mirror": "● staged" if fi["exists"] else "● not staged",
                      "Rows": fi["rows"], "Updated": fi["mtime"].strftime("%Y-%m-%d %H:%M") if fi["mtime"] else None,
                      "Purpose": purpose})
    C.table(pd.DataFrame(zrows), "hdfs_zones", column_config={"Rows": st.column_config.NumberColumn(format="localized")})
    st.caption("Status reflects the local staging copy under data/. HDFS itself is only reachable from the Docker cluster.")

with tab_hive:
    st.code("""-- Active Hive tables in 'reliance_bda_db'
CREATE EXTERNAL TABLE raw_stock_prices (trade_date STRING, open_price DOUBLE, high_price DOUBLE, low_price DOUBLE,
                                        close_price DOUBLE, volume BIGINT, ticker STRING)
LOCATION '/bda/lake/raw/prices';

CREATE TABLE reliance_features (trade_date STRING, close_price DOUBLE, ema_20 DOUBLE, ema_50 DOUBLE, vwap DOUBLE,
                                rsi_14 DOUBLE, macd DOUBLE, bb_pos DOUBLE)
PARTITIONED BY (year STRING, month STRING) STORED AS ORC;

CREATE TABLE reliance_daily_scores (trade_date STRING, technical_score DOUBLE, fundamental_score DOUBLE,
                                    news_score DOUBLE, realtime_score DOUBLE, composite_score DOUBLE)
STORED AS ORC;

CREATE TABLE reliance_predictions (trade_date STRING, predicted_close DOUBLE, direction STRING, signal STRING,
                                   confidence DOUBLE)
STORED AS ORC;""", language="sql")

with tab_raw:
    clean = dl.load_clean_joined()
    feat = B["feat"]
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f"**Clean join** · {C.freshness_tag(dl.CLEAN_JOINED)}", unsafe_allow_html=True)
        if clean.empty:
            C.empty_state("No clean join", "run_pig_etl.py has not run.", dl.CLEAN_JOINED)
        else:
            C.table(clean.tail(10), "clean_joined_tail", download=True)
    with p2:
        st.markdown(f"**Features** · {C.freshness_tag(dl.CURATED_FEATURES)}", unsafe_allow_html=True)
        if feat.empty:
            C.empty_state("No features", "spark_feature_engineering.py has not run.", dl.CURATED_FEATURES)
        else:
            C.table(feat.tail(10), "features_tail", download=True)
