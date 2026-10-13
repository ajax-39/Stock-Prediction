"""
4_Backtest_Simulator.py — Backtest replay
=========================================
Day-by-day replay of next-day forecasts, signal execution and P&L. All
computations come from simulator_engine.py (unchanged); this file is
presentation only: media-player controls, a chart that draws forward, an
equity curve that fills in, trade toasts, and a tinted ledger.

Keyboard: Space = play / pause · → = next day · Home = reset
(Streamlit reserves the R key for its own rerun shortcut.)
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
from module_3_dashboard import theme as T  # noqa: E402
from module_3_dashboard.simulator_engine import compute_simulation_state, get_simulator_dataset  # noqa: E402

INITIAL_CAPITAL = 100000.0
HORIZONS = {"Past 1 month (~23 sessions)": 1, "Past 2 months (~44 sessions)": 2, "Past 3 months (~66 sessions)": 3}
SPEEDS = {"1 s": 1, "3 s": 3, "5 s": 5, "10 s": 10}

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("sim_step", 0)
ss.setdefault("is_playing", False)
ss.setdefault("speed_sec", 3)
ss.setdefault("horizon_choice", list(HORIZONS)[0])
ss.setdefault("sim_rendered_step", None)
ss.setdefault("sim_tick_armed", False)


def reset_replay() -> None:
    ss.sim_step = 0
    ss.is_playing = False
    ss.sim_rendered_step = None


# -----------------------------------------------------------------------------
# Header + horizon
# -----------------------------------------------------------------------------
h1, h2 = st.columns([2.6, 1.2], vertical_alignment="bottom")
with h1:
    C.page_title("Backtest replay", "Replays the model's next-day calls session by session, executes BUY / SELL at the close, "
                 "and marks the portfolio to market. Computations are unchanged from simulator_engine.py.")
with h2:
    chosen = st.selectbox("Backtesting horizon", list(HORIZONS), index=list(HORIZONS).index(ss.horizon_choice), key="horizon_select")
    if chosen != ss.horizon_choice:
        ss.horizon_choice = chosen
        reset_replay()
        st.rerun()

try:
    df_sim = get_simulator_dataset(horizon_months=HORIZONS[ss.horizon_choice])
except FileNotFoundError as e:
    C.empty_state("Simulator data missing", str(e), "data/curated/reliance_features.csv · reliance_daily_scores.csv")
    st.stop()
total_steps = len(df_sim)
if total_steps == 0:
    C.empty_state("No sessions to replay", "The curated features file has no rows for this horizon.")
    st.stop()
ss.sim_step = max(0, min(ss.sim_step, total_steps - 1))
step = ss.sim_step
state = compute_simulation_state(df_sim, step, initial_capital=INITIAL_CAPITAL)
eq = pd.DataFrame(state["equity_curve"])
running_max = eq["portfolio_value"].cummax()
drawdown = ((eq["portfolio_value"] - running_max) / running_max * 100.0)
max_dd = float(drawdown.min()) if len(drawdown) else 0.0
curr_dd = float(drawdown.iloc[-1]) if len(drawdown) else 0.0
next_date = df_sim.iloc[step + 1]["trade_date"] if step < total_steps - 1 else "next session"

# -----------------------------------------------------------------------------
# Trade toasts (only when the step actually changed)
# -----------------------------------------------------------------------------
if ss.sim_rendered_step != step:
    row = df_sim.iloc[step]
    if state["in_position"] and state["active_trade"] and state["active_trade"]["entry_date"] == state["current_date"] and row["trade_signal"] == "BUY":
        st.toast(f"BUY {state['shares_held']} @ {C.inr(state['entry_price'])} · {state['current_date']}", icon=":material/trending_up:")
    elif state["trade_ledger"] and state["trade_ledger"][-1]["exit_date"] == state["current_date"]:
        t = state["trade_ledger"][-1]
        st.toast(f"SELL @ {C.inr(t['exit_price'])} · {t['result']} {C.inr(t['pnl_rs'], sign=True)} ({C.pct(t['return_pct'])})",
                 icon=":material/trending_down:" if t["result"] == "LOSS" else ":material/check_circle:")
    ss.sim_rendered_step = step

# -----------------------------------------------------------------------------
# Media-player control bar
# -----------------------------------------------------------------------------
with st.container(border=True):
    c1, c2, c3, c4, c5, c6 = st.columns([1.9, 1.8, 1.7, 2.6, 2.6, 1.6], vertical_alignment="center")
    with c1:
        if st.button("Pause" if ss.is_playing else "Play", icon=":material/pause:" if ss.is_playing else ":material/play_arrow:",
                     type="primary" if not ss.is_playing else "secondary", width="stretch", shortcut="Space",
                     key="btn_play"):
            ss.is_playing = not ss.is_playing
            ss.sim_tick_armed = False
            st.rerun()
    with c2:
        if st.button("Next", icon=":material/skip_next:", width="stretch", disabled=ss.is_playing, shortcut="Right",
                     key="btn_next"):
            if ss.sim_step < total_steps - 1:
                ss.sim_step += 1
                st.rerun()
    with c3:
        if st.button("Reset", icon=":material/replay:", width="stretch", shortcut="Home", key="btn_reset"):
            reset_replay()
            st.rerun()
    with c4:
        speed_key = next((k for k, v in SPEEDS.items() if v == ss.speed_sec), "3 s")
        sel = st.segmented_control("Speed · 1 bar per", list(SPEEDS), default=speed_key, key="speed_ctl", label_visibility="collapsed")
        if sel and SPEEDS[sel] != ss.speed_sec:
            ss.speed_sec = SPEEDS[sel]
            ss.sim_tick_armed = False
            st.rerun()
    with c5:
        slider_val = st.slider("Timeline", 0, total_steps - 1, ss.sim_step, format="Day %d", label_visibility="collapsed", key="timeline")
        if slider_val != ss.sim_step and not ss.is_playing:
            ss.sim_step = slider_val
            st.rerun()
    with c6:
        C.html(f'<div class="ss-label" style="margin:0"><span>Day <span class="ss-num">{step + 1} / {total_steps}</span></span></div>'
               f'<div class="ss-sub ss-num" style="margin-top:2px">{C.fmt_date(state["current_date"])} · {int((step + 1) / total_steps * 100)}%</div>')
    C.html('<div class="ss-src"><span class="ss-kbd">Space</span> play / pause &nbsp; <span class="ss-kbd">→</span> next day &nbsp; '
           '<span class="ss-kbd">Home</span> reset</div>')

# -----------------------------------------------------------------------------
# Primary numbers
# -----------------------------------------------------------------------------
p1, p2, p3, p4, p5 = st.columns(5)
with p1:
    C.metric("Net P&L", state["total_pnl_rs"], key="bt_pnl", delta=state["total_pnl_pct"], delta_text="total return")
with p2:
    s_pnl = state["session_pnl_rs"]
    C.metric("Session P&L", s_pnl, key="bt_spnl", delta=state["session_pnl_pct"], delta_text="today" if s_pnl else "flat / cash")
with p3:
    C.metric("Portfolio equity", state["portfolio_value"], key="bt_eq",
             sub=f"cash {C.inr(state['current_cash'])} · {state['shares_held']} shares")
with p4:
    C.metric("Win rate", state["trade_win_rate"], fmt="pct", dec=1, key="bt_wr",
             sub=f"{state['winning_trades']} wins · {state['losing_trades']} losses · {state['completed_trades']} closed")
with p5:
    C.metric("Max drawdown", max_dd, fmt="pct", dec=2, key="bt_dd", sub=f"current {C.pct(curr_dd)} from peak")

# -----------------------------------------------------------------------------
# Price chart (draws forward) + tomorrow's call
# -----------------------------------------------------------------------------
chart_col, call_col = st.columns([1.7, 1], gap="medium")
revealed = df_sim.iloc[: step + 1]
with chart_col:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.76, 0.24])
    fig.add_trace(go.Candlestick(x=revealed["trade_date"], open=revealed["open_price"], high=revealed["high_price"],
                                 low=revealed["low_price"], close=revealed["close_price"], name="RELIANCE 1D"), row=1, col=1)
    fig.add_trace(go.Scatter(x=revealed["trade_date"], y=revealed["ema_20"], name="EMA 20",
                             line=dict(color=T.WARN, width=1.3, dash="dot")), row=1, col=1)
    for t in state["trade_ledger"]:
        fig.add_trace(go.Scatter(x=[t["entry_date"]], y=[t["entry_price"] * 0.995], mode="markers+text",
                                 marker=dict(symbol="triangle-up", size=13, color=T.UP), text=["BUY"], textposition="bottom center",
                                 textfont=dict(color=T.UP, size=10), showlegend=False, hovertemplate=f"BUY @ {C.inr(t['entry_price'])}<extra></extra>"), row=1, col=1)
        col = T.UP if t["result"] == "WIN" else T.DOWN
        fig.add_trace(go.Scatter(x=[t["exit_date"]], y=[t["exit_price"] * 1.005], mode="markers+text",
                                 marker=dict(symbol="triangle-down", size=13, color=col), text=[f"SELL {C.inr(t['pnl_rs'], 0, sign=True)}"],
                                 textposition="top center", textfont=dict(color=col, size=10), showlegend=False,
                                 hovertemplate=f"SELL @ {C.inr(t['exit_price'])} · {t['result']}<extra></extra>"), row=1, col=1)
    if state["in_position"]:
        fig.add_trace(go.Scatter(x=[state["active_trade"]["entry_date"]], y=[state["entry_price"] * 0.995], mode="markers+text",
                                 marker=dict(symbol="triangle-up", size=13, color=T.BLUE), text=["LONG"], textposition="bottom center",
                                 textfont=dict(color=T.BLUE, size=10), showlegend=False, hoverinfo="skip"), row=1, col=1)
    fig.add_trace(go.Scatter(x=[state["current_date"], next_date], y=[state["current_close"], state["predicted_close"]],
                             mode="lines+markers", line=dict(color=T.ACCENT, width=2, dash="dash"), marker=dict(size=[0, 8], color=T.ACCENT),
                             name=f"Forecast {C.inr(state['predicted_close'])}"), row=1, col=1)
    fig.add_trace(go.Scatter(x=[next_date, next_date], y=[state["lower_bound"], state["upper_bound"]], mode="lines+markers",
                             line=dict(color=T.VIOLET, width=3), marker=dict(symbol="line-ew", size=12, color=T.VIOLET),
                             name=f"±MAE band {C.inr(state['upper_bound'] - state['predicted_close'])}"), row=1, col=1)
    vol_colors = [T.UP if c >= o else T.DOWN for c, o in zip(revealed["close_price"], revealed["open_price"])]
    fig.add_trace(go.Bar(x=revealed["trade_date"], y=revealed["volume"], marker_color=vol_colors, opacity=0.7, name="Volume", showlegend=False), row=2, col=1)
    full_dates = df_sim["trade_date"].tolist()
    x_end = (pd.Timestamp(full_dates[-1]) + pd.Timedelta(days=3)).strftime("%Y-%m-%d")
    ymin, ymax = float(df_sim["low_price"].min()), float(df_sim["high_price"].max())
    pad = (ymax - ymin) * 0.12
    x_start = (pd.Timestamp(full_dates[0]) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    fig.update_layout(height=470, xaxis_rangeslider_visible=False, margin=dict(l=8, r=84, t=30, b=8), uirevision="replay")
    fig.update_xaxes(range=[x_start, x_end], showgrid=False)
    fig.update_yaxes(range=[ymin - pad, ymax + pad], tickprefix="₹", tickformat=",.0f", row=1, col=1)
    fig.update_yaxes(range=[0, float(df_sim["volume"].max()) * 1.1], row=2, col=1)
    C.chart(fig, key="bt_price")

with call_col:
    with st.container(border=True):
        sig = state["trade_signal"]
        d_rs = state["predicted_close"] - state["current_close"]
        day_d = state["current_close"] - state["prev_close"]
        day_dp = (day_d / state["prev_close"] * 100.0) if state["prev_close"] else 0.0
        if state["in_position"]:
            if step > 0 and df_sim.iloc[step]["trade_signal"] == "BUY" and df_sim.iloc[step - 1]["trade_signal"] != "BUY":
                banner = ("buy", f"<b>BUY executed</b> · {state['shares_held']} shares @ {C.inr(state['entry_price'])}")
            else:
                un = state["active_trade"]["unrealized_pnl_rs"] if state["active_trade"] else 0.0
                banner = ("hold", f"<b>Holding</b> {state['shares_held']} shares from {C.inr(state['entry_price'])} · open P&L {C.inr(un, sign=True)}")
        elif state["trade_ledger"] and state["trade_ledger"][-1]["exit_date"] == state["current_date"]:
            lt = state["trade_ledger"][-1]
            banner = ("sell", f"<b>SELL executed</b> @ {C.inr(lt['exit_price'])} · realised {C.inr(lt['pnl_rs'], sign=True)} ({lt['result']})")
        else:
            banner = ("cash", "<b>In cash</b> · 0 shares held, no market exposure")
        C.html(f"""
        <div class="ss-label"><span>Tomorrow's call</span><span class="r">target {C.fmt_date(next_date) if next_date != "next session" else next_date}</span></div>
        <div class="ss-bridge"><span>Yesterday <b>{C.inr(state['prev_close'])}</b></span><span class="arr">›</span>
          <span>Today <b>{C.inr(state['current_close'])}</b> <span class="ss-num {C.tone_for(day_d)}">{C.glyph_for(day_d)} {C.pct(day_dp)}</span></span><span class="arr">›</span>
          <span>Tomorrow <b class="ss-accent">{C.inr(state['predicted_close'])}</b></span></div>
        <div class="ss-callrow" style="margin-top:10px">
          <div>{C.hero_number_html(state['predicted_close'], key="bt_pred", cls="ss-accent")}
               <div class="ss-sub ss-num" style="color:var(--ss-text2)">{C.glyph(state['predicted_direction'])} {C.inr(d_rs, 2, sign=True)} ({C.pct(state['expected_return_pct'])})</div></div>
          {C.signal_badge_html(sig, "lg")}
        </div>
        <div class="ss-kv" style="margin-top:10px">
          <span class="k">Forecast cone</span><span class="v">{C.inr(state['lower_bound'])} – {C.inr(state['upper_bound'])}</span>
          <span class="k">Confidence</span><span class="v">{C.num(state['confidence_pct'], 1)}%</span>
          <span class="k">Position</span><span class="v">{state['shares_held']} shares</span>
        </div>
        <div class="ss-banner {banner[0]}">{banner[1]}</div>
        <div class="ss-src">{C.esc(state['model_rationale'])}</div>
        """)
    d1, d2 = st.columns(2)
    comp = state["composite_score"]
    rsi = state["rsi_14"]
    tech = state["technical_score"]
    vwap_diff = ((state["current_close"] - state["vwap"]) / state["vwap"]) * 100.0 if state["vwap"] else 0.0
    with d1:
        C.metric("Composite", comp, fmt="num", dec=1, key="bt_comp", delta=comp - 50.0, delta_fmt="num", delta_text="vs neutral 50",
                 sub=C.band_label(comp))
        C.metric("RSI 14", rsi, fmt="num", dec=1, key="bt_rsi",
                 sub="overbought (>70)" if rsi > 70 else ("oversold (<35)" if rsi < 35 else "healthy (35–70)"))
    with d2:
        C.metric("Technical", tech, fmt="num", dec=1, key="bt_tech", sub="bullish momentum" if tech >= 55 else "bearish drift")
        C.metric("VWAP spread", vwap_diff, fmt="pct", dec=2, key="bt_vwap",
                 sub="above VWAP (support)" if vwap_diff > 0 else "below VWAP (resistance)")

# -----------------------------------------------------------------------------
# Equity curve + ledger
# -----------------------------------------------------------------------------
eq_col, led_col = st.columns([1.15, 1], gap="medium")
with eq_col:
    C.section("Portfolio equity", "strategy vs passive buy & hold · anchored at ₹1,00,000")
    first_close = float(df_sim.iloc[0]["close_price"])
    bh = [(INITIAL_CAPITAL / first_close) * c for c in eq["close_price"]]
    bh_pct = (bh[-1] - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100.0
    eq_fig = go.Figure()
    eq_fig.add_trace(go.Scatter(x=eq["trade_date"], y=eq["portfolio_value"], mode="lines+markers", name="Strategy",
                                line=dict(color=T.UP if state["total_pnl_rs"] >= 0 else T.DOWN, width=2.4), marker=dict(size=4),
                                fill="tozeroy", fillcolor="rgba(34,197,94,0.08)" if state["total_pnl_rs"] >= 0 else "rgba(242,85,90,0.08)",
                                hovertemplate="%{x}<br>₹%{y:,.2f}<extra>strategy</extra>"))
    eq_fig.add_trace(go.Scatter(x=eq["trade_date"], y=bh, mode="lines", name=f"Buy & hold ({C.pct(bh_pct)})",
                                line=dict(color=T.TEXT2, width=1.4, dash="dash"), hovertemplate="%{x}<br>₹%{y:,.2f}<extra>buy & hold</extra>"))
    eq_fig.add_hline(y=INITIAL_CAPITAL, line=dict(color=T.BORDER2, width=1, dash="dot"), annotation_text="₹1,00,000 baseline",
                     annotation_position="bottom right", annotation_font=dict(size=10, color=T.MUTED))
    min_eq = min(float(eq["portfolio_value"].min()), min(bh))
    max_eq = max(float(eq["portfolio_value"].max()), max(bh))
    eq_fig.update_layout(height=320, margin=dict(l=8, r=88, t=30, b=8), uirevision="replay",
                         yaxis=dict(range=[min(98000.0, min_eq - 500), max(106000.0, max_eq + 800)], tickprefix="₹", tickformat=","),
                         xaxis=dict(range=[full_dates[0], full_dates[-1]], showgrid=False))
    C.chart(eq_fig, key="bt_equity")
    alpha = state["total_pnl_pct"] - bh_pct
    C.note(f"Strategy <b class='ss-num'>{C.pct(state['total_pnl_pct'])}</b> vs buy & hold <b class='ss-num'>{C.pct(bh_pct)}</b> → "
           f"alpha <b class='ss-num'>{C.pct(alpha)}</b> over {step + 1} sessions · max drawdown {C.pct(max_dd)}.",
           kind="info" if alpha >= 0 else "warn")

with led_col:
    C.section("Trade ledger", f"{state['completed_trades']} closed · {'1 open' if state['in_position'] else 'none open'} · {state['shares_held'] or 75} shares per trade")
    if state["active_trade"] is not None:
        at = state["active_trade"]
        C.html(f"""
        <div class="ss-card tight accent" style="margin-bottom:10px">
          <div class="ss-label"><span>Open position</span><span class="r">since {C.fmt_date(at['entry_date'])}</span></div>
          <div class="ss-tile-row"><div><div class="ss-val">{at['shares']} × {C.inr(at['entry_price'])}</div>
            <div class="ss-sub">now {C.inr(at['current_price'])}</div></div>
            <div style="text-align:right"><div class="ss-val {C.tone_for(at['unrealized_pnl_rs'])}">{C.inr(at['unrealized_pnl_rs'], sign=True)}</div>
            <div class="ss-delta {C.tone_for(at['unrealized_pnl_rs'])}">{C.pct(at['unrealized_return_pct'])} unrealised</div></div></div>
        </div>""")
    else:
        C.html('<div class="ss-banner cash" style="margin:0 0 10px">No open position · 100% cash, waiting for the next BUY signal.</div>')
    if not state["trade_ledger"]:
        C.empty_state("No closed trades yet", "The ledger fills in as SELL orders execute during the replay.")
    else:
        ledger = pd.DataFrame(state["trade_ledger"])
        view = pd.DataFrame({
            "#": ledger["trade_id"], "Entry": ledger["entry_date"], "Exit": ledger["exit_date"],
            "Buy (₹)": ledger["entry_price"], "Sell (₹)": ledger["exit_price"],
            "P&L (₹)": ledger["pnl_rs"], "Return %": ledger["return_pct"], "Result": ledger["result"],
        })

        def _tint(row):
            color = "rgba(34,197,94,0.13)" if row["Result"] == "WIN" else "rgba(242,85,90,0.13)"
            return [f"background-color: {color}"] * len(row)

        st.dataframe(view.style.apply(_tint, axis=1).format({"Buy (₹)": "{:,.2f}", "Sell (₹)": "{:,.2f}", "P&L (₹)": "{:+,.2f}", "Return %": "{:+.2f}%"}),
                     width="stretch", hide_index=True, height=min(60 + 36 * len(view), 330),
                     column_config={"#": st.column_config.NumberColumn(width="small"), "Result": st.column_config.TextColumn(width="small")})
        C.csv_download(view, "trade_ledger", key="dl_ledger")

# -----------------------------------------------------------------------------
# Audit log
# -----------------------------------------------------------------------------
with st.expander("Day-by-day audit log"):
    audit = df_sim[["trade_date", "close_price", "predicted_close", "expected_return_pct", "predicted_direction", "trade_signal",
                    "confidence_pct", "actual_next_close", "actual_return_pct", "is_direction_accurate", "model_rationale"]].rename(columns={
        "trade_date": "Date", "close_price": "Close (₹)", "predicted_close": "Pred close (₹)", "expected_return_pct": "Exp ret %",
        "predicted_direction": "Dir", "trade_signal": "Signal", "confidence_pct": "Conf %", "actual_next_close": "Actual next (₹)",
        "actual_return_pct": "Act ret %", "is_direction_accurate": "Accurate?", "model_rationale": "Driver rationale"})
    st.caption(f"Direction accuracy so far: {state['correct_days']} / {state['evaluated_days']} evaluated days = {state['model_accuracy_pct']:.1f}%")
    C.table(audit, "backtest_audit_log", column_config={
        "Close (₹)": st.column_config.NumberColumn(format="₹%.2f"), "Pred close (₹)": st.column_config.NumberColumn(format="₹%.2f"),
        "Actual next (₹)": st.column_config.NumberColumn(format="₹%.2f"), "Exp ret %": st.column_config.NumberColumn(format="%+.2f%%"),
        "Act ret %": st.column_config.NumberColumn(format="%+.2f%%"), "Conf %": st.column_config.NumberColumn(format="%.0f%%")})

# -----------------------------------------------------------------------------
# Playback: a timer fragment advances one step per tick without blocking the UI
# -----------------------------------------------------------------------------
if ss.is_playing:
    if ss.sim_step >= total_steps - 1:
        ss.is_playing = False
        st.toast(f"Replay complete · net P&L {C.inr(state['total_pnl_rs'], sign=True)} ({C.pct(state['total_pnl_pct'])})", icon=":material/flag:")
        C.note(f"<b>Replay complete.</b> Reached the end of the horizon with net P&L {C.inr(state['total_pnl_rs'], sign=True)} "
               f"({C.pct(state['total_pnl_pct'])}), win rate {C.num(state['trade_win_rate'], 1)}%.", kind="info")
    else:
        ss.sim_tick_armed = False

        @st.fragment(run_every=ss.speed_sec)
        def _tick():
            if not ss.sim_tick_armed:
                ss.sim_tick_armed = True  # first call is synchronous; only timer calls advance
                return
            if ss.is_playing and ss.sim_step < total_steps - 1:
                ss.sim_step += 1
            else:
                ss.is_playing = False
            st.rerun()

        _tick()
