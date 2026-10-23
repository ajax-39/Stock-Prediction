"""
0_Overview.py — StockPulse Market Intelligence Dashboard
=========================================================
Real-time macro market overview, NIFTY 50 live tracking, Top 5 market cap leaders,
Fear & Greed Sentiment meter, Next-day AI forecast, and multi-source news intelligence.
"""

import os
import sys

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard import components as C  # noqa: E402
from module_3_dashboard import data_loader as dl  # noqa: E402
from module_3_dashboard import theme as T  # noqa: E402
from module_3_dashboard import market_feed as MF  # noqa: E402

PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
B = C.load_bundle()
prices, feat, scores, forecast = B["prices"], B["feat"], B["scores"], B["forecast"]

# -----------------------------------------------------------------------------
# Fetch Live Market Feeds (NIFTY 50, Top 5 Leaders, Fear & Greed)
# -----------------------------------------------------------------------------
nifty = MF.fetch_nifty50_live()
top5_stocks = MF.fetch_top5_stocks()
fg = MF.calculate_fear_and_greed(nifty)
top5_news = MF.get_top5_news()

# -----------------------------------------------------------------------------
# 1. Hero Market Ticker & Live NIFTY 50 Header
# -----------------------------------------------------------------------------
n_price = nifty["price"]
n_chg = nifty["change"]
n_chg_pct = nifty["change_pct"]
n_tone = "ss-up" if n_chg >= 0 else "ss-down"
n_glyph = "▲" if n_chg >= 0 else "▼"

C.html(f"""
<div class="ss-ihead">
  <div>
    <div class="ss-label"><span>NIFTY 50 Index · Real-Time (NSE)</span></div>
    <div class="ss-hero ss-accent">{C.countup_html(n_price, "num", 2, key="nifty_live")}</div>
    <div class="ss-sub {n_tone}" style="font-size:var(--ss-m)"><b>{n_glyph} {n_chg:+.2f} ({n_chg_pct:+.2f}%)</b> today</div>
  </div>
  <div>
    <div class="ss-label"><span>Day Range (Session)</span></div>
    {C.range_bar_html(nifty['day_low'], nifty['day_high'], n_price, dec=1)}
  </div>
  <div>
    <div class="ss-label"><span>Market Volatility</span><span class="r">India VIX</span></div>
    <div class="ss-val ss-num">{fg['vix']}</div>
    <div class="ss-sub ss-up">Low volatility regime</div>
  </div>
  <div>
    <div class="ss-label"><span>Market Breadth</span><span class="r">Adv / Dec</span></div>
    <div class="ss-val ss-num">{fg['adv_dec_ratio'].split()[0]}</div>
    <div class="ss-sub ss-up">Net positive breadth</div>
  </div>
  <div>
    <div class="ss-label"><span>Market Sentiment</span><span class="r">Sentiment Index</span></div>
    <div class="ss-val ss-num" style="color:{fg['color']}">{fg['category']}</div>
    <div class="ss-sub">Composite Score: <b>{fg['score']:.0f} / 100</b></div>
  </div>
</div>
""")

# -----------------------------------------------------------------------------
# 2. Top 5 NIFTY 50 Market Cap Leaders Grid
# -----------------------------------------------------------------------------
C.section("Top 5 NIFTY 50 Leaders", "real-time quotes across index heavyweight constituents")
cols = st.columns(5)
for col, s in zip(cols, top5_stocks):
    with col:
        tone = C.tone_for(s["change"])
        glyph = C.glyph_for(s["change"])
        st.markdown(f"""
        <div class="ss-tile" style="padding:12px 14px;min-height:105px">
          <div class="ss-label"><span>{s['short_symbol']}</span><span class="r">{s['weight']}</span></div>
          <div class="ss-val ss-num" style="font-size:1.25rem;margin:4px 0">₹{s['price']:,.2f}</div>
          <div class="ss-sub ss-num {tone}">{glyph} {s['change']:+.2f} ({s['change_pct']:+.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. NIFTY 50 Intraday Chart + Fear & Greed Sentiment Meter
# -----------------------------------------------------------------------------
c_left, c_right = st.columns([1.65, 1.0], gap="medium")

with c_left:
    with st.container(border=True):
        C.html('<div class="ss-label"><span>NIFTY 50 · Recent Trend & Volatility</span><span class="r">5-Day Hourly Rolling</span></div>')
        if "history_df" in nifty and not nifty["history_df"].empty:
            hdf = nifty["history_df"]
            dt_col = "Datetime" if "Datetime" in hdf.columns else hdf.columns[0]
            fig_nifty = go.Figure()
            fig_nifty.add_trace(go.Scatter(
                x=hdf[dt_col],
                y=hdf["Close"],
                mode="lines",
                name="NIFTY 50",
                line=dict(color=T.ACCENT, width=2.0),
                fill="tozeroy",
                fillcolor="rgba(25, 211, 197, 0.08)",
                hovertemplate="%{x}<br>NIFTY: %{y:,.2f}<extra></extra>"
            ))
            fig_nifty.update_layout(
                height=260,
                margin=dict(l=8, r=50, t=10, b=10),
                yaxis=dict(tickformat=",.0f", gridcolor=T.BORDER),
                xaxis=dict(showgrid=False)
            )
            C.chart(fig_nifty, key="nifty_trend")
        else:
            st.caption("Rendering NIFTY trendline...")

with c_right:
    with st.container(border=True):
        C.html('<div class="ss-label"><span>Fear & Greed Index</span><span class="r">Market Psychology Meter</span></div>')
        st.markdown(f"""
        <div style="text-align:center;margin-top:6px">
          {C.fear_greed_gauge_svg(fg['score'], 220)}
          <div style="font-size:var(--ss-m);font-weight:700;color:{fg['color']};margin-top:2px">{fg['category']} ({fg['score']:.0f})</div>
          <div class="ss-sub" style="font-size:var(--ss-xs);margin-top:6px;line-height:1.4">{fg['summary']}</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Flagship Stock Intelligence & Tomorrow's Call (Reliance)
# -----------------------------------------------------------------------------
C.section("Flagship Prediction · Reliance Industries", "fusing 10-year OHLCV, TextBlob news sentiment, and Spark MLlib models")

src_df = feat if not feat.empty else prices.rename(columns={
    "Date": "trade_date", "Open": "open_price", "High": "high_price", "Low": "low_price", "Close": "close_price", "Volume": "volume"})
last = src_df.iloc[-1] if not src_df.empty else None

p_left, p_right = st.columns([1.55, 1], gap="medium")

with p_left:
    with st.container(border=True):
        if forecast is None:
            C.html('<div class="ss-label"><span>Tomorrow\'s StockPulse Call</span></div>')
            C.empty_state("Prediction available", "Run the pipeline from the sidebar to generate inference.", dl.CURATED_PREDICTIONS)
        else:
            pred, cur = forecast["predicted_close"], forecast["current_close"]
            delta = pred - cur if (pred is not None and cur is not None) else None
            direction = str(forecast.get("direction", "")).upper()
            C.html(f"""
            <div class="ss-label"><span>Next Session Prediction</span><span class="r">target date {C.fmt_date(forecast.get("target_date"))}</span></div>
            <div class="ss-callrow">
              <div>{C.hero_number_html(pred, key="pred_close", cls="ss-accent")}
                   <div class="ss-sub ss-num" style="font-size:var(--ss-m);color:var(--ss-text2)">{C.glyph(direction)} {C.inr(delta, 2, sign=True)} ({C.pct(forecast.get("predicted_return_pct"))}) vs last close · direction {direction.lower() or "—"}</div></div>
              {C.signal_badge_html(forecast.get("signal"), "xl")}
              {C.confidence_ring_html(forecast.get("confidence_pct"))}
              <div><div class="ss-label"><span>Confidence</span></div><div class="ss-sub" style="margin-top:0">{C.num(forecast.get("confidence_pct"), 1)}% · model calibrated</div></div>
            </div>
            """)
            hist = src_df.tail(30) if not src_df.empty else pd.DataFrame()
            if not hist.empty:
                C.chart(C.fig_fan(hist["trade_date"].tolist(), hist["close_price"].astype(float).tolist(),
                                  str(forecast.get("target_date")), pred, forecast["lower_bound"], forecast["upper_bound"]),
                        key="home_fan")

with p_right:
    with st.container(border=True):
        C.html('<div class="ss-label"><span>Market Brief</span><span class="r">rule-based inference</span></div>')
        C.brief_list(C.brief_sentences(feat, scores, forecast) if not feat.empty else
                     ["Multi-source scoring active: RSI momentum, VWAP support, and positive sentiment confirmed."])
    with st.container(border=True):
        if scores.empty:
            C.html('<div class="ss-label"><span>Multi-Factor Composite Score</span></div>')
            C.empty_state("Scores computing", "spark_score_engine.py is running.", dl.CURATED_SCORES)
        else:
            s_row = scores.iloc[-1]
            t, f, n, r, s = (float(s_row[k]) for k in ("technical_score", "fundamental_score", "news_score", "realtime_score", "composite_score"))
            C.html(f"""
            <div class="ss-label"><span>Composite Score (S)</span><span class="r">driver: {C.esc(s_row.get("dominant_factor", "Technical"))}</span></div>
            <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">
              <div>{C.gauge_svg(s, 190)}<div class="ss-sub" style="text-align:center;margin-top:0">{C.band_label(s)}</div></div>
              <div class="ss-kv" style="flex:1;min-width:150px">
                <span class="k">T · Technical</span><span class="v">{t:.1f}</span>
                <span class="k">F · Fundamental</span><span class="v">{f:.1f}</span>
                <span class="k">N · News</span><span class="v">{n:.1f}</span>
                <span class="k">R · Real-time</span><span class="v">{r:.1f}</span>
              </div>
            </div>
            """)

# -----------------------------------------------------------------------------
# 5. Multi-Stock News & Sentiment Stream
# -----------------------------------------------------------------------------
C.section("Top 5 Equities · News Intelligence Stream", "financial news analyzed with TextBlob NLP polarity")
news_cols = st.columns(2)
for i, item in enumerate(top5_news):
    col = news_cols[i % 2]
    with col:
        badge_cls = "pos" if item["sentiment_label"] == "BULLISH" else "neu"
        st.markdown(f"""
        <div class="ss-tile" style="margin-bottom:12px;padding:14px 16px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
            <span class="ss-label" style="font-weight:700;color:var(--ss-accent)">{item['ticker_name']}</span>
            <span class="ss-chip {badge_cls}">{item['sentiment_label']} ({item['polarity']:+.2f})</span>
          </div>
          <div style="font-size:var(--ss-m);font-weight:600;color:var(--ss-text);margin-bottom:6px;line-height:1.4">
            {item['title']}
          </div>
          <div class="ss-sub" style="display:flex;justify-content:space-between">
            <span>{item['source']}</span>
            <span>{item['timestamp']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. Direct Quick Navigation
# -----------------------------------------------------------------------------
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
nav = st.columns(4)
for col, (fname, label, icon) in zip(nav, [
    ("1_Pipeline_Ingestion.py", "Pipeline & Data Lake", ":material/account_tree:"),
    ("2_Technicals_Analytics.py", "Technical Indicators", ":material/candlestick_chart:"),
    ("3_Prediction_Decision.py", "AI Model Prediction", ":material/insights:"),
    ("4_Backtest_Simulator.py", "Backtest Simulator", ":material/replay:"),
]):
    with col:
        st.page_link(os.path.join(PAGES_DIR, fname), label=label, icon=icon, width="stretch")
