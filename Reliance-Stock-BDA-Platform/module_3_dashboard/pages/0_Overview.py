"""
0_Overview.py — Stock sight home
================================
The answer in five seconds: last close, tomorrow's call, why, and whether the
data can be trusted. Every number is computed from the files on disk.
"""

import os
import sys

import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard import components as C  # noqa: E402
from module_3_dashboard import data_loader as dl  # noqa: E402
from module_3_dashboard import theme as T  # noqa: E402

PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
B = C.load_bundle()
prices, feat, scores, forecast = B["prices"], B["feat"], B["scores"], B["forecast"]

if feat.empty and prices.empty:
    C.page_title("Overview", T.TAGLINE)
    C.empty_state("No price data yet", "Run the pipeline from the sidebar to ingest prices and build features.", dl.RAW_PRICES)
    st.stop()

src_df = feat if not feat.empty else prices.rename(columns={
    "Date": "trade_date", "Open": "open_price", "High": "high_price", "Low": "low_price", "Close": "close_price", "Volume": "volume"})
last = src_df.iloc[-1]
prev = src_df.iloc[-2] if len(src_df) >= 2 else None
as_of = str(last["trade_date"])
last_close = float(last["close_price"])
day_chg = last_close - float(prev["close_price"]) if prev is not None else None
day_chg_pct = (day_chg / float(prev["close_price"]) * 100.0) if prev is not None else None

# 52-week range and volume context from the raw price history (fallback: features)
px = prices.rename(columns={"Low": "low_price", "High": "high_price", "Volume": "volume"}) if not prices.empty else src_df
tail = px.tail(252)
lo52, hi52 = float(tail["low_price"].min()), float(tail["high_price"].max())
vol20 = float(px["volume"].tail(20).mean())
vol_last = float(px["volume"].iloc[-1])
vol_spark = px["volume"].tail(20).tolist()
vol_ratio = vol_last / vol20 if vol20 else None

# -----------------------------------------------------------------------------
# Instrument header (one grid, five cells)
# -----------------------------------------------------------------------------
if day_chg is None:
    chg_cell = '<div class="ss-label"><span>Day change</span></div><div class="ss-val">—</div><div class="ss-sub">needs two sessions</div>'
else:
    chg_cell = (f'<div class="ss-label"><span>Day change</span></div>'
                f'<div class="ss-val {C.tone_for(day_chg)}">{C.glyph_for(day_chg)} {C.countup_html(day_chg, "inr", 2, key="day_chg", sign=True)}</div>'
                f'<div class="ss-sub ss-num {C.tone_for(day_chg)}">{C.pct(day_chg_pct)} vs {C.fmt_date(prev["trade_date"])}</div>')
vol_delta = (f'<div class="ss-delta"><span class="{C.tone_for(vol_ratio - 1)}">{C.countup_html(vol_ratio, "x", 2, key="vol_ratio")} the 20-day average</span></div>'
             if vol_ratio else "")
C.html(f"""
<div class="ss-ihead">
  <div><div class="ss-label"><span>Last close · Reliance Industries</span></div>{C.hero_number_html(last_close, key="last_close")}
       <div class="ss-sub">{C.fmt_date(as_of)} · {C.freshness_tag(dl.RAW_PRICES)}</div></div>
  <div>{chg_cell}</div>
  <div><div class="ss-label"><span>Day range</span></div>{C.range_bar_html(float(last["low_price"]), float(last["high_price"]), last_close)}</div>
  <div><div class="ss-label"><span>52-week range</span><span class="r">{len(tail)} sessions</span></div>{C.range_bar_html(lo52, hi52, last_close, accent=True)}</div>
  <div><div class="ss-label"><span>Volume</span><span class="r">last 20 sessions</span></div>
       <div class="ss-tile-row"><div><div class="ss-val">{C.compact_in(vol_last)}</div>{vol_delta}</div><div>{C.sparkline_svg(vol_spark, w=64, h=28)}</div></div></div>
</div>
""")

# -----------------------------------------------------------------------------
# Tomorrow's call · brief · composite gauge
# -----------------------------------------------------------------------------
left, right = st.columns([1.55, 1], gap="medium")

with left:
    with st.container(border=True):
        if forecast is None:
            C.html('<div class="ss-label"><span>Tomorrow\'s call</span></div>')
            C.empty_state("No forecast yet", "predict_next_day.py has not written a prediction. Run the pipeline.", dl.CURATED_PREDICTIONS)
        else:
            pred, cur = forecast["predicted_close"], forecast["current_close"]
            delta = pred - cur if (pred is not None and cur is not None) else None
            direction = str(forecast.get("direction", "")).upper()
            C.html(f"""
            <div class="ss-label"><span>Tomorrow's call</span><span class="r">target {C.fmt_date(forecast.get("target_date"))}</span></div>
            <div class="ss-callrow">
              <div>{C.hero_number_html(pred, key="pred_close", cls="ss-accent")}
                   <div class="ss-sub ss-num" style="font-size:var(--ss-m);color:var(--ss-text2)">{C.glyph(direction)} {C.inr(delta, 2, sign=True)} ({C.pct(forecast.get("predicted_return_pct"))}) vs last close · direction {direction.lower() or "—"}</div></div>
              {C.signal_badge_html(forecast.get("signal"), "xl")}
              {C.confidence_ring_html(forecast.get("confidence_pct"))}
              <div><div class="ss-label"><span>Confidence</span></div><div class="ss-sub" style="margin-top:0">{C.num(forecast.get("confidence_pct"), 1)}% · model floor is 55</div></div>
            </div>
            """)
            hist = src_df.tail(30)
            C.chart(C.fig_fan(hist["trade_date"].tolist(), hist["close_price"].astype(float).tolist(),
                              str(forecast.get("target_date")), pred, forecast["lower_bound"], forecast["upper_bound"]),
                    key="home_fan")
            C.source_note(f'Last 30 closes + forecast with ±MAE band ({C.inr(forecast.get("mae_range"))}) · from '
                          f'<code>{forecast["_source"]}</code> · created {C.fmt_date(forecast.get("created_at"), "%d %b %Y %H:%M")}')

with right:
    with st.container(border=True):
        C.html('<div class="ss-label"><span>Today\'s brief</span><span class="r">rule-based, from the latest row</span></div>')
        C.brief_list(C.brief_sentences(feat, scores, forecast) if not feat.empty else
                     ["Feature file missing: run the pipeline for indicator-based sentences."])
    with st.container(border=True):
        if scores.empty:
            C.html('<div class="ss-label"><span>Composite score</span></div>')
            C.empty_state("No scores yet", "spark_score_engine.py has not run.", dl.CURATED_SCORES)
        else:
            s_row = scores.iloc[-1]
            t, f, n, r, s = (float(s_row[k]) for k in ("technical_score", "fundamental_score", "news_score", "realtime_score", "composite_score"))
            C.html(f"""
            <div class="ss-label"><span>Composite score</span><span class="r">dominant: {C.esc(s_row.get("dominant_factor", "—"))}</span></div>
            <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap">
              <div>{C.gauge_svg(s, 190)}<div class="ss-sub" style="text-align:center;margin-top:0">{C.band_label(s)}</div></div>
              <div class="ss-kv" style="flex:1;min-width:150px">
                <span class="k">T · Technical</span><span class="v">{t:.1f}</span>
                <span class="k">F · Fundamental</span><span class="v">{f:.1f}</span>
                <span class="k">N · News</span><span class="v">{n:.1f}</span>
                <span class="k">R · Real-time</span><span class="v">{r:.1f}</span>
              </div>
            </div>
            <div class="ss-src">{C.freshness_tag(dl.CURATED_SCORES)}</div>
            """)

# -----------------------------------------------------------------------------
# How the score adds up (waterfall) · signal thresholds
# -----------------------------------------------------------------------------
if not scores.empty:
    s_row = scores.iloc[-1]
    t, f, n, r, s = (float(s_row[k]) for k in ("technical_score", "fundamental_score", "news_score", "realtime_score", "composite_score"))
    with st.container(border=True):
        C.html('<div class="ss-label"><span>How the score adds up</span><span class="r">S = 0.40·T + 0.20·F + 0.25·N + 0.15·R · thresholds from predict_next_day.py</span></div>')
        C.chart(C.fig_waterfall(t, f, n, r, height=240), key="home_wf")

# -----------------------------------------------------------------------------
# Pipeline health strip + quick navigation
# -----------------------------------------------------------------------------
C.section("Pipeline health", "status read from the files on disk")
C.stage_strip(dl.pipeline_stages())
serving = B["serving"]
if forecast and serving and isinstance(serving[0], dict):
    cf = serving[0].get("cf_pred", {}) or {}
    try:
        hb_pred = float(cf.get("predicted_close", "nan"))
    except (TypeError, ValueError):
        hb_pred = float("nan")
    if cf and (abs(hb_pred - float(forecast["predicted_close"])) > 1.0 or str(cf.get("signal", "")).upper() != str(forecast.get("signal", "")).upper()):
        C.note(f'The HBase mock\'s latest <code>cf_pred</code> holds <b>{C.inr(hb_pred)} / {C.esc(cf.get("signal", "—"))}</b> (placeholder defaults '
               f'written by the streaming stage), while <code>{forecast["_source"]}</code> says <b>{C.inr(forecast["predicted_close"])} / '
               f'{C.esc(forecast.get("signal"))}</b>. Stock sight reads the predictions file everywhere.', kind="warn")

nav = st.columns(4)
for col, (fname, label, icon) in zip(nav, [
    ("1_Pipeline_Ingestion.py", "Pipeline & Data", ":material/account_tree:"),
    ("2_Technicals_Analytics.py", "Technicals", ":material/candlestick_chart:"),
    ("3_Prediction_Decision.py", "Prediction", ":material/insights:"),
    ("4_Backtest_Simulator.py", "Backtest", ":material/replay:"),
]):
    with col:
        st.page_link(os.path.join(PAGES_DIR, fname), label=label, icon=icon, width="stretch")

# -----------------------------------------------------------------------------
# News & sentiment
# -----------------------------------------------------------------------------
news = B["news"]
C.section("News & sentiment", f"{len(news)} headlines · TextBlob polarity" if not news.empty else "no headlines")
if news.empty:
    C.empty_state("No news rows", "news_curated_feed.py has not written any headlines.", dl.RAW_NEWS)
else:
    q = dl.data_quality_report().get("news_match")
    if q and q["total"] and q["matched"] == 0:
        C.note(f'News is dated <b>{C.fmt_date(q["news_min"])} – {C.fmt_date(q["news_max"])}</b> but prices end '
               f'<b>{C.fmt_date(q["price_max"])}</b>: <b>{q["matched"]} of {q["total"]}</b> headlines join to a trading day, '
               f'so the news score N stays flat at 50.', kind="warn")
    elif q and q["total"]:
        C.note(f'{q["matched"]} of {q["total"]} headlines join to a trading day ({q["rate_pct"]}%).', kind="info")
    C.news_cards(news.sort_values("trade_date", ascending=False) if "trade_date" in news.columns else news)
