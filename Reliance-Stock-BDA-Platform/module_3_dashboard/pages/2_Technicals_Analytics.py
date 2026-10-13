"""
2_Technicals_Analytics.py — Technical Analysis
==============================================
Interactive technical chart with indicators, multi-factor scores,
and momentum analysis for Reliance Industries stock.
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard.styles import CUSTOM_CSS
from module_3_dashboard.data_loader import (
    load_engineered_features,
    load_daily_scores,
    load_sector_momentum
)

st.set_page_config(page_title="Technical Analysis — Reliance Analytics", page_icon="📊", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("Technical Analysis")
st.markdown("Interactive price charts, technical indicators, and multi-factor scoring for Reliance Industries.")

df_feat = load_engineered_features()
df_sc = load_daily_scores()
df_mom = load_sector_momentum()

if df_feat.empty or df_sc.empty:
    st.warning("Technical data not found. Run the processing pipeline to generate indicators.")
    st.stop()

# -----------------------------------------------------------------------------
# Technical Chart with Indicators
# -----------------------------------------------------------------------------
st.markdown("## Price & Indicators")

# Time range and indicator controls
col_ctrl1, col_ctrl2 = st.columns([1, 3])
with col_ctrl1:
    time_window = st.selectbox(
        "Time Range",
        ["60 Days", "180 Days", "1 Year", "All Data"],
        index=1
    )

window_map = {
    "60 Days": 60,
    "180 Days": 180,
    "1 Year": 252,
    "All Data": len(df_feat)
}
slice_n = min(len(df_feat), window_map[time_window])
plot_df = df_feat.tail(slice_n).copy()

# Indicator toggles
with col_ctrl2:
    st.markdown("**Overlays:**")
    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        show_ema20 = st.checkbox("EMA 20", value=False)
    with col_t2:
        show_ema50 = st.checkbox("EMA 50", value=False)
    with col_t3:
        show_vwap = st.checkbox("VWAP", value=False)
    with col_t4:
        show_bb = st.checkbox("Bollinger Bands", value=False)

# Create 4-row subplot: 1. Candlestick+Overlays, 2. Volume, 3. RSI, 4. MACD
fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.02,
    row_heights=[0.50, 0.16, 0.17, 0.17]
)

# Row 1: Candlestick
fig.add_trace(go.Candlestick(
    x=plot_df["trade_date"],
    open=plot_df["open_price"],
    high=plot_df["high_price"],
    low=plot_df["low_price"],
    close=plot_df["close_price"],
    name="RELIANCE",
    increasing_line_color="#22C55E",
    decreasing_line_color="#EF4444",
    increasing_fillcolor="#22C55E",
    decreasing_fillcolor="#EF4444"
), row=1, col=1)

# Overlays (conditional based on toggles)
if show_ema20:
    fig.add_trace(go.Scatter(
        x=plot_df["trade_date"], y=plot_df["ema_20"],
        name="EMA 20",
        line=dict(color="#60A5FA", width=1.5)
    ), row=1, col=1)

if show_ema50:
    fig.add_trace(go.Scatter(
        x=plot_df["trade_date"], y=plot_df["ema_50"],
        name="EMA 50",
        line=dict(color="#F59E0B", width=1.5)
    ), row=1, col=1)

if show_vwap:
    fig.add_trace(go.Scatter(
        x=plot_df["trade_date"], y=plot_df["vwap"],
        name="VWAP",
        line=dict(color="#A855F7", width=1.5, dash="dash")
    ), row=1, col=1)

if show_bb:
    fig.add_trace(go.Scatter(
        x=plot_df["trade_date"], y=plot_df["bb_upper"],
        name="BB Upper",
        line=dict(color="#929BAD", width=1, dash="dot"),
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=plot_df["trade_date"], y=plot_df["bb_lower"],
        name="BB Lower",
        line=dict(color="#929BAD", width=1, dash="dot"),
        fill="tonexty",
        fillcolor="rgba(146, 155, 173, 0.05)"
    ), row=1, col=1)

# Row 2: Volume
colors_vol = ['#22C55E' if c >= o else '#EF4444' for c, o in zip(plot_df["close_price"], plot_df["open_price"])]
fig.add_trace(go.Bar(
    x=plot_df["trade_date"],
    y=plot_df["volume"],
    name="Volume",
    marker_color=colors_vol,
    opacity=0.6,
    showlegend=False
), row=2, col=1)

# Row 3: RSI
fig.add_trace(go.Scatter(
    x=plot_df["trade_date"],
    y=plot_df["rsi_14"],
    name="RSI",
    line=dict(color="#60A5FA", width=1.5),
    showlegend=False
), row=3, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="#EF4444", line_width=1, row=3, col=1, annotation_text="Overbought", annotation_position="right")
fig.add_hline(y=30, line_dash="dot", line_color="#22C55E", line_width=1, row=3, col=1, annotation_text="Oversold", annotation_position="right")

# Row 4: MACD
fig.add_trace(go.Scatter(
    x=plot_df["trade_date"],
    y=plot_df["macd"],
    name="MACD",
    line=dict(color="#60A5FA", width=1.2),
    showlegend=False
), row=4, col=1)
fig.add_trace(go.Scatter(
    x=plot_df["trade_date"],
    y=plot_df["macd_signal"],
    name="Signal",
    line=dict(color="#F59E0B", width=1.2),
    showlegend=False
), row=4, col=1)
colors_hist = ['#22C55E' if h >= 0 else '#EF4444' for h in plot_df["macd_hist"]]
fig.add_trace(go.Bar(
    x=plot_df["trade_date"],
    y=plot_df["macd_hist"],
    name="Histogram",
    marker_color=colors_hist,
    opacity=0.6,
    showlegend=False
), row=4, col=1)

fig.update_layout(
    height=800,
    xaxis_rangeslider_visible=False,
    paper_bgcolor="#0B0E14",
    plot_bgcolor="#121722",
    font=dict(color="#929BAD", family="Inter", size=10),
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(
        orientation="h",
        yanchor="top",
        y=1.02,
        xanchor="left",
        x=0,
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=10)
    ),
    hovermode="x unified"
)

# Update all axes
for i in range(1, 5):
    fig.update_xaxes(gridcolor="#273142", showgrid=True, zeroline=False, row=i, col=1)
    fig.update_yaxes(gridcolor="#273142", showgrid=True, zeroline=False, side="right", row=i, col=1)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# Indicator Summary Table
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("## Indicator Summary")

latest_feat = plot_df.iloc[-1]
latest_score = df_sc.iloc[-1]

# Technical indicator interpretations
rsi_val = float(latest_feat["rsi_14"])
rsi_interp = "Overbought" if rsi_val > 70 else ("Oversold" if rsi_val < 30 else "Neutral")

macd_val = float(latest_feat["macd"])
macd_sig = float(latest_feat["macd_signal"])
macd_interp = "Bullish crossover" if macd_val > macd_sig else "Bearish crossover"

ema20 = float(latest_feat["ema_20"])
ema50 = float(latest_feat["ema_50"])
ema_interp = "Short-term uptrend" if ema20 > ema50 else "Short-term downtrend"

bb_pos = float(latest_feat["bb_pos"])
bb_interp = "Upper band" if bb_pos > 0.8 else ("Lower band" if bb_pos < 0.2 else "Mid-range")

indicator_data = {
    "Indicator": ["RSI (14)", "MACD", "EMA 20 vs 50", "Bollinger Band Position"],
    "Value": [f"{rsi_val:.1f}", f"{macd_val:.2f}", f"{ema20:,.0f} vs {ema50:,.0f}", f"{bb_pos:.2f}"],
    "Interpretation": [rsi_interp, macd_interp, ema_interp, bb_interp]
}

df_indicators = pd.DataFrame(indicator_data)
st.dataframe(df_indicators, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# Multi-Factor Scores
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("## Multi-Factor Scores")
st.markdown("Composite scoring combining technical, fundamental, news sentiment, and real-time signals.")

t_val = float(latest_score["technical_score"])
f_val = float(latest_score["fundamental_score"])
n_val = float(latest_score["news_score"])
r_val = float(latest_score["realtime_score"])
s_val = float(latest_score["composite_score"])
dominant = latest_score.get("dominant_factor", "Technical")

col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns(5)

with col_s1:
    st.metric("Technical", f"{t_val:.1f}/100", "Indicators")
with col_s2:
    st.metric("Fundamental", f"{f_val:.1f}/100", "Valuation")
with col_s3:
    st.metric("News Sentiment", f"{n_val:.1f}/100", "NLP")
with col_s4:
    st.metric("Real-time", f"{r_val:.1f}/100", "Streaming")
with col_s5:
    st.metric("Composite", f"{s_val:.1f}/100", f"Driven by {dominant}")

st.caption("Composite score formula: S = 0.40·T + 0.20·F + 0.25·N + 0.15·R")

# -----------------------------------------------------------------------------
# Sector Momentum (if available)
# -----------------------------------------------------------------------------
if not df_mom.empty:
    st.markdown("---")
    st.markdown("## Momentum Analysis")
    st.markdown("Rolling momentum indices calculated via distributed MapReduce processing.")
    
    latest_mom = df_mom.iloc[-1]
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("30-Day Momentum", f"{latest_mom['ret_30d']:+.2f}%", "Short-term")
    with m_col2:
        st.metric("60-Day Momentum", f"{latest_mom['ret_60d']:+.2f}%", "Medium-term")
    with m_col3:
        st.metric("90-Day Momentum", f"{latest_mom['ret_90d']:+.2f}%", "Long-term")
    with m_col4:
        st.metric("Volume Trend", f"{latest_mom['vol_trend']:.2f}x", "vs 20-day avg")

