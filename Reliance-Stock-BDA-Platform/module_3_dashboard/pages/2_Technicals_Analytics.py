"""
2_Technicals_Analytics.py — Technicals
======================================
One price chart with toggleable overlays and synced volume / RSI / MACD panels,
an indicator summary that reads value → state → effect on the score, the
multi-factor scores, momentum, and a calendar of daily returns.
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

C.page_title("Technicals", "Price with EMA 20/50, VWAP and Bollinger overlays, synced volume, RSI 14 and MACD panels, "
             "and how each indicator feeds the technical score T.")

if feat.empty:
    C.empty_state("Technical features not found", "Run spark_feature_engineering.py to build indicators.", dl.CURATED_FEATURES)
    st.stop()

# -----------------------------------------------------------------------------
# Controls
# -----------------------------------------------------------------------------
ctl1, ctl2, ctl3 = st.columns([1.7, 2, 1.4], vertical_alignment="bottom")
with ctl1:
    rng = st.segmented_control("Range", ["60D", "180D", "1Y", "All", "Custom"], default="180D", key="tech_range")
with ctl2:
    overlays = st.pills("Overlays", ["EMA 20", "EMA 50", "VWAP", "Bollinger Bands"], selection_mode="multi",
                        default=["EMA 20"], key="tech_overlays") or []
with ctl3:
    if rng == "Custom":
        plot_df = C.date_range_filter(feat, "trade_date", key="tech_custom", default_days=120, label="From – to")
    else:
        n = {"60D": 60, "180D": 180, "1Y": 252, "All": len(feat)}.get(rng or "180D", 180)
        plot_df = feat.tail(min(n, len(feat)))
        st.caption(f"{len(plot_df):,} sessions · {C.fmt_date(plot_df['trade_date'].iloc[0])} – {C.fmt_date(plot_df['trade_date'].iloc[-1])}")

if plot_df.empty:
    C.empty_state("No sessions in range", "Widen the date range.")
    st.stop()

# -----------------------------------------------------------------------------
# Main chart: candles + overlays | volume | RSI | MACD (shared x)
# -----------------------------------------------------------------------------
fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.025, row_heights=[0.52, 0.14, 0.17, 0.17])
x = plot_df["trade_date"]
fig.add_trace(go.Candlestick(x=x, open=plot_df["open_price"], high=plot_df["high_price"], low=plot_df["low_price"],
                             close=plot_df["close_price"], name="RELIANCE"), row=1, col=1)
if "EMA 20" in overlays:
    fig.add_trace(go.Scatter(x=x, y=plot_df["ema_20"], name="EMA 20", line=dict(color=T.BLUE, width=1.4)), row=1, col=1)
if "EMA 50" in overlays:
    fig.add_trace(go.Scatter(x=x, y=plot_df["ema_50"], name="EMA 50", line=dict(color=T.WARN, width=1.4)), row=1, col=1)
if "VWAP" in overlays:
    fig.add_trace(go.Scatter(x=x, y=plot_df["vwap"], name="VWAP", line=dict(color=T.VIOLET, width=1.4, dash="dash")), row=1, col=1)
if "Bollinger Bands" in overlays:
    fig.add_trace(go.Scatter(x=x, y=plot_df["bb_upper"], name="BB upper", line=dict(color=T.MUTED, width=1, dash="dot"), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=plot_df["bb_lower"], name="Bollinger", line=dict(color=T.MUTED, width=1, dash="dot"),
                             fill="tonexty", fillcolor="rgba(154,166,184,0.06)"), row=1, col=1)
vol_colors = [T.UP if c >= o else T.DOWN for c, o in zip(plot_df["close_price"], plot_df["open_price"])]
fig.add_trace(go.Bar(x=x, y=plot_df["volume"], name="Volume", marker_color=vol_colors, opacity=0.7, showlegend=False,
                     hovertemplate="%{y:,.0f}<extra>volume</extra>"), row=2, col=1)
fig.add_trace(go.Scatter(x=x, y=plot_df["rsi_14"], name="RSI 14", line=dict(color=T.ACCENT, width=1.5), showlegend=False), row=3, col=1)
fig.add_hline(y=70, line=dict(color=T.DOWN, width=1, dash="dot"), row=3, col=1, annotation_text="70 overbought", annotation_position="top left", annotation_font=dict(size=9, color=T.DOWN))
fig.add_hline(y=30, line=dict(color=T.UP, width=1, dash="dot"), row=3, col=1, annotation_text="30 oversold", annotation_position="bottom left", annotation_font=dict(size=9, color=T.UP))
fig.add_trace(go.Scatter(x=x, y=plot_df["macd"], name="MACD", line=dict(color=T.ACCENT, width=1.3), showlegend=False), row=4, col=1)
fig.add_trace(go.Scatter(x=x, y=plot_df["macd_signal"], name="Signal", line=dict(color=T.WARN, width=1.3), showlegend=False), row=4, col=1)
hist_colors = [T.UP if h >= 0 else T.DOWN for h in plot_df["macd_hist"]]
fig.add_trace(go.Bar(x=x, y=plot_df["macd_hist"], name="Histogram", marker_color=hist_colors, opacity=0.7, showlegend=False), row=4, col=1)
fig.update_layout(height=760, xaxis_rangeslider_visible=False, margin=dict(l=8, r=72, t=30, b=8),
                  xaxis4=dict(rangeselector=None))
for i, label in enumerate(["₹", "Vol", "RSI", "MACD"], start=1):
    fig.update_yaxes(title_text=label, title_standoff=4, row=i, col=1)
fig.update_yaxes(tickprefix="₹", tickformat=",.0f", row=1, col=1)
fig.update_yaxes(range=[0, 100], tickvals=[30, 50, 70], row=3, col=1)
fig.update_xaxes(showgrid=False)
fig.update_xaxes(nticks=10, row=4, col=1)
C.chart(fig, key="tech_main")

# -----------------------------------------------------------------------------
# Indicator summary: value → state → effect on T
# -----------------------------------------------------------------------------
C.section("Indicator summary", f"latest session {C.fmt_date(feat['trade_date'].iloc[-1])} · sub-scores mirror spark_score_engine.py")
latest = feat.iloc[-1]
breakdown = C.technical_breakdown(latest)
df_ind = pd.DataFrame([{"Indicator": b["indicator"], "Value": b["value"], "State": b["state"], "Sub-score": b["sub"],
                        "Effect on T": "supports" if b["sub"] >= 60 else ("drags" if b["sub"] <= 35 else "neutral")}
                       for b in breakdown])
t_calc = sum(b["sub"] for b in breakdown) / len(breakdown)
C.table(df_ind, "indicator_summary", column_config={
    "Sub-score": st.column_config.ProgressColumn("Sub-score", min_value=0, max_value=100, format="%.0f"),
})
st.caption(f"T = mean of the six sub-scores = {t_calc:.2f}" + (f" (scores file: {float(scores.iloc[-1]['technical_score']):.2f})" if not scores.empty else ""))

# -----------------------------------------------------------------------------
# Multi-factor scores
# -----------------------------------------------------------------------------
C.section("Multi-factor scores", "S = 0.40·T + 0.20·F + 0.25·N + 0.15·R")
if scores.empty:
    C.empty_state("Daily scores not found", "Run spark_score_engine.py.", dl.CURATED_SCORES)
else:
    ls = scores.iloc[-1]
    sc_hist = scores.tail(len(plot_df))
    k1, k2, k3, k4, k5 = st.columns([1, 1, 1, 1, 1.2])
    with k1:
        C.metric("T · Technical", float(ls["technical_score"]), fmt="num", dec=1, key="sc_t", delta_text="/ 100", spark=sc_hist["technical_score"].tolist())
    with k2:
        C.metric("F · Fundamental", float(ls["fundamental_score"]), fmt="num", dec=1, key="sc_f", delta_text="/ 100 · constant", spark=sc_hist["fundamental_score"].tolist())
    with k3:
        C.metric("N · News", float(ls["news_score"]), fmt="num", dec=1, key="sc_n", delta_text="/ 100", spark=sc_hist["news_score"].tolist())
    with k4:
        C.metric("R · Real-time", float(ls["realtime_score"]), fmt="num", dec=1, key="sc_r", delta_text="/ 100", spark=sc_hist["realtime_score"].tolist())
    with k5:
        C.metric("S · Composite", float(ls["composite_score"]), fmt="num", dec=1, key="sc_s",
                 delta_text=C.band_label(float(ls["composite_score"])), spark=sc_hist["composite_score"].tolist(),
                 label_right=f"dominant: {C.esc(ls.get('dominant_factor', '—'))}")
    fig_s = go.Figure()
    for col, name, color in (("technical_score", "T", T.BLUE), ("news_score", "N", T.VIOLET), ("realtime_score", "R", T.WARN), ("composite_score", "S", T.ACCENT)):
        fig_s.add_trace(go.Scatter(x=sc_hist["trade_date"], y=sc_hist[col], name=name, line=dict(color=color, width=2.2 if col == "composite_score" else 1.2)))
    fig_s.add_hrect(y0=C.BUY_MIN, y1=100, fillcolor="rgba(34,197,94,0.05)", line_width=0)
    fig_s.add_hrect(y0=0, y1=C.SELL_MAX, fillcolor="rgba(242,85,90,0.05)", line_width=0)
    fig_s.update_layout(height=240, margin=dict(l=8, r=40, t=28, b=8), yaxis=dict(range=[0, 100], tickvals=[0, C.SELL_MAX, C.BUY_MIN, C.STRONG_BUY_MIN, 100]), xaxis=dict(showgrid=False))
    C.chart(fig_s, key="tech_scores")

# -----------------------------------------------------------------------------
# Momentum (MapReduce)
# -----------------------------------------------------------------------------
C.section("Momentum", f"rolling returns from Hadoop MapReduce · {C.freshness_tag(dl.CURATED_MOMENTUM)}")
if mom.empty:
    C.empty_state("Momentum file not found", "Run run_momentum_mr.py.", dl.CURATED_MOMENTUM)
else:
    lm = mom.iloc[-1]
    mh = mom.tail(len(plot_df))
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        C.metric("30-day return", float(lm["ret_30d"]), fmt="pct", dec=2, key="mo30", spark=mh["ret_30d"].tolist(), sub="short-term")
    with m2:
        C.metric("60-day return", float(lm["ret_60d"]), fmt="pct", dec=2, key="mo60", spark=mh["ret_60d"].tolist(), sub="medium-term")
    with m3:
        C.metric("90-day return", float(lm["ret_90d"]), fmt="pct", dec=2, key="mo90", spark=mh["ret_90d"].tolist(), sub="long-term")
    with m4:
        C.metric("Volume trend", float(lm["vol_trend"]), fmt="x", dec=2, key="movt", spark=mh["vol_trend"].tolist(), sub="vs 20-day average")

# -----------------------------------------------------------------------------
# Calendar heatmap of daily returns
# -----------------------------------------------------------------------------
C.section("Daily returns calendar", "last 12 months · green up, red down")
C.chart(C.fig_calendar_heatmap(feat, months=12, height=200), key="tech_cal")
with st.expander("Indicator data in range"):
    C.table(plot_df, "features_in_range")
