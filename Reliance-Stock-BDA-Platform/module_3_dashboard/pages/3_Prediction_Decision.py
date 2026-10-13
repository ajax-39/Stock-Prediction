"""
3_Prediction_Decision.py — Prediction
=====================================
Leads with the forecast and the signal, then an honest model card against the
naive "tomorrow = today" baseline, feature importances and the prediction
history. The forecast always comes from reliance_predictions.csv.
"""

import os
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard import components as C  # noqa: E402
from module_3_dashboard import data_loader as dl  # noqa: E402
from module_3_dashboard import theme as T  # noqa: E402

B = C.load_bundle()
forecast, metrics, feat, preds, serving = B["forecast"], B["metrics"], B["feat"], B["preds"], B["serving"]

C.page_title("Prediction", "Next-day close forecast and trading signal, with the model scored honestly against the naive baseline.")

if forecast is None:
    C.empty_state("No prediction records found", "Run module_2_processing/prediction/predict_next_day.py (or the pipeline button) first.",
                  dl.CURATED_PREDICTIONS)
    st.stop()

pred, cur = forecast["predicted_close"], forecast["current_close"]
delta_rs = pred - cur
delta_pct = forecast.get("predicted_return_pct")
direction = str(forecast.get("direction", "")).upper()
signal = forecast.get("signal")
conf = forecast.get("confidence_pct")
low, high = forecast.get("lower_bound"), forecast.get("upper_bound")
comp = forecast.get("composite_score")
rowkey = serving[0].get("rowkey", "—") if serving and isinstance(serving[0], dict) else "—"

# -----------------------------------------------------------------------------
# Forecast + signal logic
# -----------------------------------------------------------------------------
left, right = st.columns([1.6, 1], gap="medium")
with left:
    with st.container(border=True):
        C.html(f"""
        <div class="ss-label"><span>Next session forecast</span><span class="r">target {C.fmt_date(forecast.get("target_date"))} · from {C.fmt_date(forecast.get("trade_date"))} close</span></div>
        <div class="ss-callrow">
          <div>{C.hero_number_html(pred, key="pred_close", cls="ss-accent")}
               <div class="ss-sub ss-num" style="font-size:var(--ss-m);color:var(--ss-text2)">{C.glyph(direction)} {C.inr(delta_rs, 2, sign=True)} ({C.pct(delta_pct)}) vs last close {C.inr(cur)} · {direction.lower() or "—"}</div></div>
          {C.signal_badge_html(signal, "xl")}
          {C.confidence_ring_html(conf)}
          <div><div class="ss-label"><span>Confidence</span></div><div class="ss-sub" style="margin-top:0">{C.num(conf, 1)}%</div></div>
          <div><div class="ss-label"><span>Interval · ±MAE</span></div><div class="ss-sub ss-num" style="margin-top:0">{C.inr(low)} – {C.inr(high)}</div></div>
        </div>
        """)
        hist = feat.tail(60) if not feat.empty else pd.DataFrame()
        if not hist.empty:
            C.chart(C.fig_fan(hist["trade_date"].tolist(), hist["close_price"].astype(float).tolist(),
                              str(forecast.get("target_date")), pred, low, high, height=250), key="pred_fan")
        C.source_note(f'from <code>{forecast["_source"]}</code> · created {C.fmt_date(forecast.get("created_at"), "%d %b %Y %H:%M")} · '
                      f'HBase rowkey <code>{C.esc(rowkey)}</code>')

with right:
    with st.container(border=True):
        C.html('<div class="ss-label"><span>Why this signal</span><span class="r">rules from predict_next_day.py</span></div>')
        ret_frac = (delta_pct or 0.0) / 100.0
        rules = []
        if comp is not None:
            rules.append(f'Composite <span class="ss-num">{comp:.2f}</span> → <b>{C.band_label(comp)}</b>.')
            rules.append(f'Predicted return = (S − 50) / 50 × 2.2% = <span class="ss-num">{C.pct(delta_pct)}</span>'
                         + (" (positive)" if ret_frac > 0 else (" (negative)" if ret_frac < 0 else " (flat)")) + ".")
            if comp >= C.STRONG_BUY_MIN and ret_frac > 0:
                fired = f"S ≥ {C.STRONG_BUY_MIN:.0f} and return > 0 → STRONG BUY"
            elif comp >= C.BUY_MIN and ret_frac > 0:
                fired = f"S ≥ {C.BUY_MIN:.0f} and return > 0 → BUY"
            elif comp <= C.SELL_MAX or ret_frac < -0.01:
                fired = f"S ≤ {C.SELL_MAX:.0f} or return < −1% → SELL"
            else:
                fired = f"neither BUY (needs S ≥ {C.BUY_MIN:.0f}) nor SELL (needs S ≤ {C.SELL_MAX:.0f} or return < −1%) → HOLD"
            rules.append(f"Rule that fired: <b>{fired}</b>.")
            calc_conf = max(55.0, min(92.0, 50.0 + abs(comp - 50.0) * 0.8))
            rules.append(f'Confidence = 50 + |S − 50| × 0.8, clamped to 55–92 → <span class="ss-num">{calc_conf:.1f}%</span>.')
        rules.append(f'Direction: {"UP" if ret_frac > 0.003 else ("DOWN" if ret_frac < -0.003 else "FLAT")} (±0.3% threshold).')
        C.brief_list(rules)
        if forecast.get("technical_score") is not None:
            C.html(f'<div class="ss-kv" style="margin-top:10px"><span class="k">T · Technical</span><span class="v">{forecast["technical_score"]:.2f}</span>'
                   f'<span class="k">N · News</span><span class="v">{forecast["news_score"]:.2f}</span>'
                   f'<span class="k">S · Composite</span><span class="v">{comp:.2f}</span></div>')

# -----------------------------------------------------------------------------
# Model card vs naive baseline
# -----------------------------------------------------------------------------
C.section("Model card", f'{C.esc(metrics.get("model_name", "model")) if metrics else "model"} · {C.freshness_tag(dl.MODEL_METRICS)}')
if not B["metrics_exists"] or not metrics:
    C.empty_state("No model metrics", "train_mllib_model.py has not written reliance_model_metrics.json; nothing to score.", dl.MODEL_METRICS)
else:
    mae, rmse = metrics.get("mae_rupees"), metrics.get("rmse_rupees")
    b_mae, b_rmse = metrics.get("baseline_mae"), metrics.get("baseline_rmse")
    dacc = metrics.get("directional_accuracy_pct")
    n_test = metrics.get("test_samples")
    mae_edge = ((b_mae - mae) / b_mae * 100.0) if (mae is not None and b_mae) else None
    rmse_edge = ((b_rmse - rmse) / b_rmse * 100.0) if (rmse is not None and b_rmse) else None
    # Sign-persistence baseline over the same test window, computed from the features file
    persist = None
    if not feat.empty and n_test:
        r = feat["daily_return"].tail(int(n_test) + 1).to_numpy()
        prev_s, cur_s = np.sign(r[:-1]), np.sign(r[1:])
        mask = (prev_s != 0) & (cur_s != 0)
        if mask.sum():
            persist = float((prev_s[mask] == cur_s[mask]).mean() * 100.0)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        C.metric("Model MAE", mae, key="mae", delta=mae_edge, delta_fmt="pct", delta_text="vs naive (positive = better)",
                 sub=f"test window {n_test} sessions" if n_test else "")
    with k2:
        C.metric("Model RMSE", rmse, key="rmse", delta=rmse_edge, delta_fmt="pct", delta_text="vs naive")
    with k3:
        C.metric("Directional accuracy", dacc, fmt="pct", dec=1, key="dacc", delta=(dacc - 50.0) if dacc is not None else None,
                 delta_fmt="num", delta_text="pts vs coin flip")
    with k4:
        C.metric("Naive MAE · tomorrow = today", b_mae, key="bmae", sub=f"naive RMSE {C.inr(b_rmse)}" if b_rmse else "")
    card = pd.DataFrame({
        "Metric": ["MAE (₹)", "RMSE (₹)", "Directional accuracy (%)"],
        "Model": [mae, rmse, dacc],
        "Naive baseline": [b_mae, b_rmse, None],
        "Sign-persistence baseline": [None, None, persist],
        "Edge": [f"{C.pct(mae_edge)} error" if mae_edge is not None else "—",
                 f"{C.pct(rmse_edge)} error" if rmse_edge is not None else "—",
                 f"{C.num(dacc - 50.0, 1, sign=True)} pts vs 50% coin flip" if dacc is not None else "—"],
    })
    C.table(card, "model_card", column_config={
        "Model": st.column_config.NumberColumn(format="%.2f"), "Naive baseline": st.column_config.NumberColumn(format="%.2f"),
        "Sign-persistence baseline": st.column_config.NumberColumn(format="%.1f")})
    verdict_bad = (mae_edge is not None and mae_edge <= 0) or (dacc is not None and dacc < 50)
    if verdict_bad:
        C.note(f"<b>The model does not beat the naive baseline on this test window.</b> MAE {C.inr(mae)} vs {C.inr(b_mae)} "
               f"({C.pct(mae_edge)}), directional accuracy {C.num(dacc, 1)}% against a 50% coin flip"
               + (f" and {persist:.1f}% for simply repeating yesterday's direction" if persist is not None else "")
               + ". Treat the forecast as a composite-score projection, not a learned edge.", kind="bad")
    else:
        C.note(f"The model beats the naive baseline: MAE {C.inr(mae)} vs {C.inr(b_mae)} ({C.pct(mae_edge)}), "
               f"directional accuracy {C.num(dacc, 1)}%.", kind="info")
    # Test window: actual close vs the naive forecast it is scored against
    if not feat.empty and n_test:
        win = feat.tail(int(n_test) + 1).copy()
        naive = win["close_price"].shift(1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=win["trade_date"], y=win["close_price"], name="Actual close", line=dict(color=T.TEXT2, width=1.6)))
        fig.add_trace(go.Scatter(x=win["trade_date"], y=naive + mae, line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=win["trade_date"], y=naive - mae, fill="tonexty", fillcolor="rgba(25,211,197,0.10)",
                                 line=dict(width=0), name="±MAE around naive", hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=win["trade_date"], y=naive, name="Naive forecast (yesterday's close)",
                                 line=dict(color=T.ACCENT, width=1.2, dash="dot")))
        fig.update_layout(height=300, yaxis=dict(tickprefix="₹", tickformat=",.0f"), xaxis=dict(showgrid=False),
                          margin=dict(l=8, r=64, t=28, b=8))
        C.chart(fig, key="pred_testwin")
        st.caption("The pipeline does not persist per-day model predictions, so only the naive baseline curve can be drawn. "
                   "The earlier 'walk-forward' chart synthesised a model curve from sine noise and has been removed.")

# -----------------------------------------------------------------------------
# Feature importances
# -----------------------------------------------------------------------------
C.section("Feature importances", "relative weight of each input in the trained model")
imps = (metrics or {}).get("feature_importances") or {}
if not imps:
    C.empty_state("No feature importances", "The metrics file has no feature_importances block.", dl.MODEL_METRICS)
else:
    f1, f2 = st.columns([1.6, 1])
    with f1:
        C.chart(C.fig_importances(imps, height=360), key="pred_imp")
    with f2:
        df_imp = pd.DataFrame(sorted(imps.items(), key=lambda kv: -kv[1]), columns=["Feature", "Importance"])
        df_imp["Importance"] = df_imp["Importance"] * 100.0
        C.table(df_imp, "feature_importances", column_config={
            "Importance": st.column_config.ProgressColumn("Importance %", min_value=0, max_value=float(df_imp["Importance"].max()), format="%.2f")})

# -----------------------------------------------------------------------------
# Prediction history + serving log
# -----------------------------------------------------------------------------
C.section("Prediction history", f'{forecast["_rows"]} record(s) in <code>{forecast["_source"]}</code>')
show_cols = [c for c in ["trade_date", "target_date", "current_close", "predicted_close", "predicted_return_pct", "lower_bound",
                         "upper_bound", "direction", "signal", "confidence_pct", "composite_score", "created_at"] if c in preds.columns]
C.table(preds[show_cols].iloc[::-1].reset_index(drop=True), "prediction_history", column_config={
    "current_close": st.column_config.NumberColumn("current close", format="₹%.2f"),
    "predicted_close": st.column_config.NumberColumn("predicted close", format="₹%.2f"),
    "lower_bound": st.column_config.NumberColumn("lower", format="₹%.2f"),
    "upper_bound": st.column_config.NumberColumn("upper", format="₹%.2f"),
    "predicted_return_pct": st.column_config.NumberColumn("return %", format="%+.2f%%"),
    "confidence_pct": st.column_config.NumberColumn("confidence %", format="%.1f%%"),
})
with st.expander(f"Serving log · HBase mock ({len(serving)} rows)"):
    if not serving:
        C.empty_state("No serving rows", "hbase_loader.py has not written the mock.", dl.SERVING_MOCK)
    else:
        rows = []
        for rec in serving:
            if not isinstance(rec, dict):
                continue
            tick, sc, cp = rec.get("cf_tick", {}) or {}, rec.get("cf_score", {}) or {}, rec.get("cf_pred", {}) or {}
            rows.append({"rowkey": rec.get("rowkey"), "created_at": rec.get("created_at"), "ltp": tick.get("ltp"),
                         "tick volume": tick.get("volume"), "R": sc.get("R"), "composite": sc.get("composite"),
                         "cf_pred close": cp.get("predicted_close"), "cf_pred signal": cp.get("signal"), "cf_pred mae": cp.get("mae_range")})
        df_srv = pd.DataFrame(rows)
        for c in ("ltp", "tick volume", "R", "composite", "cf_pred close", "cf_pred mae"):
            if c in df_srv.columns:
                df_srv[c] = pd.to_numeric(df_srv[c], errors="coerce")
        st.caption("cf_pred values in these rows are written by the streaming stage with placeholder defaults; the forecast above never reads them.")
        C.table(df_srv, "serving_log", height=320)
