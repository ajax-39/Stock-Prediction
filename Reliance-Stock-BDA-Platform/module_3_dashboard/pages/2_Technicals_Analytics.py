"""
2_Technicals_Analytics.py — Technical Indicators & Multi-Factor Score Cockpit
=============================================================================
Interactive Plotly Candlestick chart with EMA, VWAP, Bollinger Bands, Volume,
RSI, and MACD subplots, radial gauge indicators for 4 scores (T, F, N, R),
and MapReduce rolling momentum indices.
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

st.set_page_config(page_title="Technicals & Analytics — RELIANCE BDA", page_icon="📊", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("📊 Module 2: Technical Indicators & Multi-Factor Analytics")
st.markdown("Engineered quantitative features and multi-factor algorithmic scoring for **Reliance Industries Ltd (RELIANCE.NS)**.")

df_feat = load_engineered_features()
df_sc = load_daily_scores()
df_mom = load_sector_momentum()

if df_feat.empty or df_sc.empty:
    st.warning("Features or daily scores not found. Run module_2_processing pipeline scripts first.")
    st.stop()

# -----------------------------------------------------------------------------
# Section 1: Multi-Factor Score Radial Gauges (T, F, N, R -> Composite S)
# -----------------------------------------------------------------------------
st.subheader("🎯 Multi-Factor Algorithmic Health Scores")

latest_score = df_sc.iloc[-1]
t_val = float(latest_score["technical_score"])
f_val = float(latest_score["fundamental_score"])
n_val = float(latest_score["news_score"])
r_val = float(latest_score["realtime_score"])
s_val = float(latest_score["composite_score"])
dominant = latest_score.get("dominant_factor", "Technical")


def create_radial_gauge(value: float, title: str, color: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 14, 'color': '#9ca3af'}},
        number={'font': {'size': 24, 'color': '#f9fafb'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#374151', 'tickfont': {'color': '#6b7280', 'size': 9}},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': 'rgba(31, 41, 55, 0.4)',
            'borderwidth': 1,
            'bordercolor': 'rgba(255, 255, 255, 0.1)',
            'steps': [
                {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [40, 60], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [60, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ]
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=15, r=15, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


g_col1, g_col2, g_col3, g_col4, g_col5 = st.columns([1, 1, 1, 1, 1.2])
with g_col1:
    st.plotly_chart(create_radial_gauge(t_val, "Technical (T)", "#38bdf8"), use_container_width=True)
with g_col2:
    st.plotly_chart(create_radial_gauge(f_val, "Fundamental (F)", "#a78bfa"), use_container_width=True)
with g_col3:
    st.plotly_chart(create_radial_gauge(n_val, "News NLP (N)", "#34d399"), use_container_width=True)
with g_col4:
    st.plotly_chart(create_radial_gauge(r_val, "Streaming Tick (R)", "#f59e0b"), use_container_width=True)

with g_col5:
    st.markdown(f"""
    <div class="glass-card" style="height:180px; display:flex; flex-direction:column; justify-content:center; text-align:center;">
        <div style="font-size:0.8rem; color:#9ca3af; font-weight:600;">COMPOSITE SCORE (S)</div>
        <div style="font-size:2.4rem; font-weight:800; color:#10b981; margin:4px 0;">{s_val:.1f} <span style="font-size:1rem; color:#6b7280;">/ 100</span></div>
        <div style="font-size:0.78rem; color:#9ca3af;">
            Dominant Driver: <strong style="color:#38bdf8;">{dominant}</strong>
        </div>
        <div style="font-size:0.7rem; color:#6b7280; margin-top:4px;">
            S = 0.40·T + 0.20·F + 0.25·N + 0.15·R
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Section 2: Interactive Plotly Candlestick & Indicator Subplots
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("📈 Multi-Subplot Technical Chart Studio")

chart_filter_col1, chart_filter_col2 = st.columns([1, 3])
with chart_filter_col1:
    time_window = st.selectbox(
        "Time Horizon:",
        ["Last 60 Days", "Last 180 Days", "Last 1 Year (365d)", "Full 2010-2025 History"],
        index=1
    )

window_map = {
    "Last 60 Days": 60,
    "Last 180 Days": 180,
    "Last 1 Year (365d)": 252,
    "Full 2010-2025 History": len(df_feat)
}
slice_n = min(len(df_feat), window_map[time_window])
plot_df = df_feat.tail(slice_n).copy()

# Create 4-row subplot: 1. Candlestick+EMA+VWAP+BB, 2. Volume, 3. RSI, 4. MACD
fig = make_subplots(
    rows=4, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.50, 0.16, 0.17, 0.17],
    subplot_titles=(
        "Price (Candlestick, EMA 20/50, VWAP, Bollinger Bands)",
        "Volume & 20-Day Average",
        "Relative Strength Index (RSI 14)",
        "MACD (12, 26, 9) Histogram"
    )
)

# Row 1: Candlestick
fig.add_trace(go.Candlestick(
    x=plot_df["trade_date"],
    open=plot_df["open_price"],
    high=plot_df["high_price"],
    low=plot_df["low_price"],
    close=plot_df["close_price"],
    name="RELIANCE",
    increasing_line_color="#10b981",
    decreasing_line_color="#ef4444"
), row=1, col=1)

# Overlays
fig.add_trace(go.Scatter(x=plot_df["trade_date"], y=plot_df["ema_20"], name="EMA 20", line=dict(color="#38bdf8", width=1.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=plot_df["trade_date"], y=plot_df["ema_50"], name="EMA 50", line=dict(color="#f59e0b", width=1.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=plot_df["trade_date"], y=plot_df["vwap"], name="VWAP", line=dict(color="#a855f7", width=1.5, dash="dash")), row=1, col=1)
fig.add_trace(go.Scatter(x=plot_df["trade_date"], y=plot_df["bb_upper"], name="BB Upper", line=dict(color="rgba(156, 163, 175, 0.4)", width=1)), row=1, col=1)
fig.add_trace(go.Scatter(x=plot_df["trade_date"], y=plot_df["bb_lower"], name="BB Lower", line=dict(color="rgba(156, 163, 175, 0.4)", width=1), fill="tonexty", fillcolor="rgba(156, 163, 175, 0.05)"), row=1, col=1)

# Row 2: Volume
colors_vol = ['#10b981' if c >= o else '#ef4444' for c, o in zip(plot_df["close_price"], plot_df["open_price"])]
fig.add_trace(go.Bar(x=plot_df["trade_date"], y=plot_df["volume"], name="Volume", marker_color=colors_vol, opacity=0.8), row=2, col=1)

# Row 3: RSI
fig.add_trace(go.Scatter(x=plot_df["trade_date"], y=plot_df["rsi_14"], name="RSI (14)", line=dict(color="#38bdf8", width=1.5)), row=3, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="#ef4444", line_width=1, row=3, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="#10b981", line_width=1, row=3, col=1)

# Row 4: MACD
fig.add_trace(go.Scatter(x=plot_df["trade_date"], y=plot_df["macd"], name="MACD", line=dict(color="#38bdf8", width=1.2)), row=4, col=1)
fig.add_trace(go.Scatter(x=plot_df["trade_date"], y=plot_df["macd_signal"], name="Signal", line=dict(color="#f59e0b", width=1.2)), row=4, col=1)
colors_hist = ['#10b981' if h >= 0 else '#ef4444' for h in plot_df["macd_hist"]]
fig.add_trace(go.Bar(x=plot_df["trade_date"], y=plot_df["macd_hist"], name="Histogram", marker_color=colors_hist), row=4, col=1)

fig.update_layout(
    height=800,
    xaxis_rangeslider_visible=False,
    paper_bgcolor="rgba(17, 24, 39, 0.8)",
    plot_bgcolor="rgba(10, 14, 23, 0.8)",
    font=dict(color="#9ca3af", family="Inter"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# Section 3: MapReduce Rolling Sector Momentum View
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("⚡ Hadoop MapReduce: Rolling Sector Momentum Indices")

if not df_mom.empty:
    latest_mom = df_mom.iloc[-1]
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("30-Day Momentum Return", f"{latest_mom['ret_30d']:+.2f}%", "Hadoop MapReduce")
    with m_col2:
        st.metric("60-Day Momentum Return", f"{latest_mom['ret_60d']:+.2f}%", "Hadoop MapReduce")
    with m_col3:
        st.metric("90-Day Momentum Return", f"{latest_mom['ret_90d']:+.2f}%", "Hadoop MapReduce")
    with m_col4:
        st.metric("20-Day Volume Trend", f"{latest_mom['vol_trend']:.2f}x", "Relative to 20d SMA")
