"""
2_Technicals_Analytics.py — Technical Indicators & Quantitative Analytics
========================================================================
Technical scoring gauge at the top, followed by multi-overlay candlestick charts,
synchronized volume/RSI/MACD panels, and indicator summary breakdown at the bottom.
"""

import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard import components as C  # noqa: E402
from module_3_dashboard import data_loader as dl  # noqa: E402
from module_3_dashboard import theme as T  # noqa: E402

B = C.load_bundle()
feat, scores, mom = B["feat"], B["scores"], B["momentum"]

C.page_title("Technical Indicators & Analytics", "PySpark SQL window functions computing EMA, VWAP, RSI, MACD, and Bollinger Bands.")

if feat.empty:
    C.empty_state("Technical features not found", "Run spark_feature_engineering.py to build indicators.", dl.CURATED_FEATURES)
    st.stop()

# -----------------------------------------------------------------------------
# 1. TOP SECTION: Multi-Factor Scoring Engine & Technical Score Gauge Meter
# -----------------------------------------------------------------------------
C.section("Multi-Factor Scoring Engine", "S = 0.40·T + 0.20·F + 0.25·N + 0.15·R · Technical score weighted at 40%")

latest_feat = feat.iloc[-1]
breakdown = C.technical_breakdown(latest_feat)
t_val = float(scores.iloc[-1]["technical_score"]) if not scores.empty else (sum(b["sub"] for b in breakdown) / len(breakdown))

g_col1, g_col2 = st.columns([1.1, 1.9], gap="medium")

with g_col1:
    with st.container(border=True):
        st.markdown("<div class='ss-label' style='text-align:center'><span>Technical Health Score (T)</span></div>", unsafe_allow_html=True)
        fig_meter = C.technical_meter_fig(t_val, width=320, height=195)
        C.chart(fig_meter, key="tech_gauge_meter")
        state_t = "Bullish Momentum" if t_val >= 60 else ("Neutral / Indecisive" if t_val >= 40 else "Bearish Drag")
        st.markdown(f"<div style='text-align:center;font-size:var(--ss-s);font-weight:600;color:var(--ss-accent);margin-top:-10px'>{state_t}</div>", unsafe_allow_html=True)

with g_col2:
    with st.container(border=True):
        st.markdown("<div class='ss-label'><span>Component Score Summary</span><span class='r'>Normalized to 0–100</span></div>", unsafe_allow_html=True)
        if not scores.empty:
            ls = scores.iloc[-1]
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                C.metric("T · Technical", float(ls["technical_score"]), fmt="num", dec=1, key="top_sc_t", delta_text="weight 40%")
            with k2:
                C.metric("F · Fundamental", float(ls["fundamental_score"]), fmt="num", dec=1, key="top_sc_f", delta_text="weight 20%")
            with k3:
                C.metric("N · News", float(ls["news_score"]), fmt="num", dec=1, key="top_sc_n", delta_text="weight 25%")
            with k4:
                C.metric("R · Real-time", float(ls["realtime_score"]), fmt="num", dec=1, key="top_sc_r", delta_text="weight 15%")
            
            comp = float(ls["composite_score"])
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:14px;padding:10px 14px;background:rgba(25,211,197,0.06);border:1px solid var(--ss-border);border-radius:6px">
              <div>
                <span style="font-size:var(--ss-xs);text-transform:uppercase;color:var(--ss-muted);letter-spacing:0.05em">Composite Decision Score (S)</span>
                <div style="font-size:1.4rem;font-weight:700;color:var(--ss-accent)" class="ss-num">{comp:.2f} / 100</div>
              </div>
              <div style="text-align:right">
                <span class="ss-chip pos" style="font-size:var(--ss-s)">{C.signal_band(comp)} BAND</span>
                <div class="ss-sub" style="margin-top:4px">Primary driver: <b>{ls.get('dominant_factor', 'Technical')}</b></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. Controls & Date Filtering
# -----------------------------------------------------------------------------
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
ctl1, ctl2 = st.columns([1.25, 1.75], vertical_alignment="bottom")
with ctl1:
    rng = st.segmented_control("Range", ["60D", "180D", "1Y", "All", "Custom"], default="180D", key="tech_range")
with ctl2:
    overlays = st.pills("Overlays", ["EMA 20", "EMA 50", "VWAP", "Bollinger Bands"], selection_mode="multi",
                        default=["EMA 20", "VWAP"], key="tech_overlays") or []

if rng == "Custom":
    plot_df = C.date_range_filter(feat, "trade_date", key="tech_custom", default_days=120, label="From – to")
else:
    n = {"60D": 60, "180D": 180, "1Y": 252, "All": len(feat)}.get(rng or "180D", 180)
    plot_df = feat.tail(min(n, len(feat)))

if plot_df.empty:
    C.empty_state("No sessions in range", "Widen the date range.")
    st.stop()

# -----------------------------------------------------------------------------
# 3. MIDDLE SECTION: Main Chart (Candlesticks + Overlays | Volume | RSI | MACD)
# -----------------------------------------------------------------------------
C.section("Interactive Technical Price Chart", f"{len(plot_df):,} trading sessions · synchronized with Volume, RSI 14, and MACD (12, 26, 9)")

fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.025, row_heights=[0.52, 0.14, 0.17, 0.17])
x = plot_df["trade_date"]

# Candlestick chart
fig.add_trace(go.Candlestick(
    x=x, open=plot_df["open_price"], high=plot_df["high_price"], low=plot_df["low_price"],
    close=plot_df["close_price"], name="Price"
), row=1, col=1)

# Overlays
if "EMA 20" in overlays:
    fig.add_trace(go.Scatter(x=x, y=plot_df["ema_20"], name="EMA 20", line=dict(color=T.BLUE, width=1.4)), row=1, col=1)
if "EMA 50" in overlays:
    fig.add_trace(go.Scatter(x=x, y=plot_df["ema_50"], name="EMA 50", line=dict(color=T.WARN, width=1.4)), row=1, col=1)
if "VWAP" in overlays:
    fig.add_trace(go.Scatter(x=x, y=plot_df["vwap"], name="VWAP", line=dict(color=T.VIOLET, width=1.4, dash="dash")), row=1, col=1)
if "Bollinger Bands" in overlays:
    fig.add_trace(go.Scatter(x=x, y=plot_df["bb_upper"], name="BB Upper", line=dict(color=T.MUTED, width=1, dash="dot"), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=plot_df["bb_lower"], name="Bollinger", line=dict(color=T.MUTED, width=1, dash="dot"),
                             fill="tonexty", fillcolor="rgba(154,166,184,0.06)"), row=1, col=1)

# Volume
vol_colors = [T.UP if c >= o else T.DOWN for c, o in zip(plot_df["close_price"], plot_df["open_price"])]
fig.add_trace(go.Bar(x=x, y=plot_df["volume"], name="Volume", marker_color=vol_colors, opacity=0.7, showlegend=False,
                     hovertemplate="%{y:,.0f}<extra>volume</extra>"), row=2, col=1)

# RSI (14)
fig.add_trace(go.Scatter(x=x, y=plot_df["rsi_14"], name="RSI 14", line=dict(color=T.ACCENT, width=1.5), showlegend=False), row=3, col=1)
fig.add_hline(y=70, line=dict(color=T.DOWN, width=1, dash="dot"), row=3, col=1, annotation_text="70 overbought", annotation_position="top left", annotation_font=dict(size=9, color=T.DOWN))
fig.add_hline(y=30, line=dict(color=T.UP, width=1, dash="dot"), row=3, col=1, annotation_text="30 oversold", annotation_position="bottom left", annotation_font=dict(size=9, color=T.UP))

# MACD
fig.add_trace(go.Scatter(x=x, y=plot_df["macd"], name="MACD", line=dict(color=T.ACCENT, width=1.3), showlegend=False), row=4, col=1)
fig.add_trace(go.Scatter(x=x, y=plot_df["macd_signal"], name="Signal", line=dict(color=T.WARN, width=1.3), showlegend=False), row=4, col=1)
hist_colors = [T.UP if h >= 0 else T.DOWN for h in plot_df["macd_hist"]]
fig.add_trace(go.Bar(x=x, y=plot_df["macd_hist"], name="Histogram", marker_color=hist_colors, opacity=0.7, showlegend=False), row=4, col=1)

fig.update_layout(height=720, xaxis_rangeslider_visible=False, margin=dict(l=8, r=72, t=20, b=8), xaxis4=dict(rangeselector=None))
for i, label in enumerate(["₹", "Vol", "RSI", "MACD"], start=1):
    fig.update_yaxes(title_text=label, title_standoff=4, row=i, col=1)
fig.update_yaxes(tickprefix="₹", tickformat=",.0f", row=1, col=1)
fig.update_yaxes(range=[0, 100], tickvals=[30, 50, 70], row=3, col=1)
fig.update_xaxes(showgrid=False)
fig.update_xaxes(nticks=10, row=4, col=1)
C.chart(fig, key="tech_main_chart")

# -----------------------------------------------------------------------------
# 4. BOTTOM SECTION: Indicator Summary Table & Sub-Score Breakdown
# -----------------------------------------------------------------------------
C.section("Indicator Summary & Sub-Score Contribution", f"latest session {C.fmt_date(feat['trade_date'].iloc[-1])} · individual weights feeding Technical Score T")
df_ind = pd.DataFrame([
    {"Indicator": b["indicator"], "Value": b["value"], "State": b["state"], "Sub-score": b["sub"],
     "Impact on T": "● Bullish (+)" if b["sub"] >= 60 else ("● Bearish (–)" if b["sub"] <= 35 else "● Neutral")}
    for b in breakdown
])
C.table(df_ind, "indicator_summary_table", column_config={
    "Sub-score": st.column_config.ProgressColumn("Sub-score (0–100)", min_value=0, max_value=100, format="%.0f"),
})

# -----------------------------------------------------------------------------
# 5. MapReduce Momentum & 12-Month Calendar
# -----------------------------------------------------------------------------
c_m1, c_m2 = st.columns([1, 1], gap="medium")
with c_m1:
    C.section("Rolling Sector Momentum", "Hadoop MapReduce streaming analytics")
    if not mom.empty:
        lm = mom.iloc[-1]
        m1, m2, m3 = st.columns(3)
        with m1:
            C.metric("30-Day Return", float(lm["ret_30d"]), fmt="pct", dec=2, key="tech_mo30")
        with m2:
            C.metric("60-Day Return", float(lm["ret_60d"]), fmt="pct", dec=2, key="tech_mo60")
        with m3:
            C.metric("90-Day Return", float(lm["ret_90d"]), fmt="pct", dec=2, key="tech_mo90")

with c_m2:
    C.section("Daily Returns Calendar", "12-month historical distribution")
    C.chart(C.fig_calendar_heatmap(feat, months=12, height=180), key="tech_calendar")
