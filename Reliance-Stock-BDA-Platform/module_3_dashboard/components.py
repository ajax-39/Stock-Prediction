"""
components.py — Reusable Stock sight UI helpers
==============================================
Pages compose these helpers instead of writing HTML/CSS. Every helper reads its
colours and fonts from theme.py. Helpers whose name ends in `_html` return a
string; the others render straight to Streamlit.
"""

from __future__ import annotations

import datetime as dt
import html as _html
import math
import os
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from module_3_dashboard import theme as T
from module_3_dashboard import data_loader as dl

# =============================================================================
# Formatting (Indian number system, signed percentages, relative times)
# =============================================================================
MINUS = "−"  # U+2212, renders at the same width as "+"


def _is_nan(x) -> bool:
    try:
        return x is None or (isinstance(x, float) and math.isnan(x))
    except Exception:
        return False


def group_indian(int_str: str) -> str:
    if len(int_str) <= 3:
        return int_str
    head, tail = int_str[:-3], int_str[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts) + "," + tail


def inr(x, dec: int = 2, sign: bool = False, symbol: str = "₹") -> str:
    """₹1,23,456.78 — Indian grouping, true minus sign, optional forced +."""
    if _is_nan(x):
        return "—"
    x = float(x)
    neg = x < 0
    s = f"{abs(x):.{dec}f}"
    ip, _, fp = s.partition(".")
    out = symbol + group_indian(ip) + (f".{fp}" if dec else "")
    if neg:
        return MINUS + out
    return ("+" + out) if sign else out


def num(x, dec: int = 2, sign: bool = False) -> str:
    return inr(x, dec=dec, sign=sign, symbol="")


def pct(x, dec: int = 2, sign: bool = True) -> str:
    """Always signed percentage: +0.15% / −1.48%."""
    if _is_nan(x):
        return "—"
    x = float(x)
    body = f"{abs(x):.{dec}f}%"
    if x < 0:
        return MINUS + body
    return ("+" + body) if sign else body


def compact_in(x) -> str:
    """Volume / money in Indian compact units: 1.16 Cr, 45.2 L, 9,100."""
    if _is_nan(x):
        return "—"
    x = float(x)
    a = abs(x)
    if a >= 1e7:
        s = f"{a / 1e7:.2f} Cr"
    elif a >= 1e5:
        s = f"{a / 1e5:.2f} L"
    else:
        s = group_indian(f"{a:.0f}")
    return (MINUS if x < 0 else "") + s


def fmt_date(d, fmt: str = "%d %b %Y") -> str:
    if d is None or (isinstance(d, float) and math.isnan(d)):
        return "—"
    try:
        return pd.to_datetime(d).strftime(fmt)
    except Exception:
        return str(d)


def ago(ts: dt.datetime | None) -> str:
    if ts is None:
        return "never"
    delta = dt.datetime.now() - ts
    s = int(delta.total_seconds())
    if s < 60:
        return "just now"
    if s < 3600:
        return f"{s // 60} min ago"
    if s < 86400:
        return f"{s // 3600} h ago"
    return f"{s // 86400} d ago"


def glyph(direction: str | None) -> str:
    return T.DIRECTION_GLYPH.get(str(direction).upper(), "▬")


def glyph_for(value: float) -> str:
    if _is_nan(value) or abs(float(value)) < 1e-12:
        return "▬"
    return "▲" if float(value) > 0 else "▼"


def tone_for(value: float) -> str:
    """CSS class for a signed number."""
    if _is_nan(value) or abs(float(value)) < 1e-12:
        return "ss-neutral"
    return "ss-up" if float(value) > 0 else "ss-down"


def signal_class(signal: str | None) -> str:
    s = str(signal or "").upper()
    if "BUY" in s:
        return "buy"
    if s == "SELL":
        return "sell"
    if s == "HOLD":
        return "hold"
    return "neutral"


def esc(s) -> str:
    return _html.escape(str(s), quote=True)


# =============================================================================
# Signal thresholds (mirrors module_2_processing/prediction/predict_next_day.py)
# =============================================================================
STRONG_BUY_MIN = 75.0
BUY_MIN = 60.0
SELL_MAX = 35.0
SELL_RET = -1.0  # predicted return % below which SELL fires regardless of score
COMPOSITE_WEIGHTS = {"T": 0.40, "F": 0.20, "N": 0.25, "R": 0.15}


def signal_band(score: float) -> str:
    if score >= STRONG_BUY_MIN:
        return "STRONG BUY"
    if score >= BUY_MIN:
        return "BUY"
    if score <= SELL_MAX:
        return "SELL"
    return "HOLD"


def band_label(score: float) -> str:
    if score >= STRONG_BUY_MIN:
        return f"STRONG BUY band (≥{STRONG_BUY_MIN:.0f})"
    if score >= BUY_MIN:
        return f"BUY band ({BUY_MIN:.0f}–{STRONG_BUY_MIN:.0f})"
    if score <= SELL_MAX:
        return f"SELL band (≤{SELL_MAX:.0f})"
    return f"HOLD band ({SELL_MAX:.0f}–{BUY_MIN:.0f})"


# =============================================================================
# Low-level render helpers
# =============================================================================
def html(markup: str) -> None:
    """
    Render trusted HTML. st.html() runs DOMPurify with the html-only profile, which
    strips inline <svg>, so this goes through st.markdown with the indentation
    removed (indented lines would otherwise become code blocks).
    """
    cleaned = "".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def inject_css() -> None:
    st.markdown(T.CUSTOM_CSS, unsafe_allow_html=True)


def countup_html(value: float, fmt: str = "inr", dec: int = 2, key: str | None = None,
                 sign: bool = False, cls: str = "") -> str:
    """A number that counts up on load. Server renders the final text, JS animates."""
    if _is_nan(value):
        return f'<span class="ss-num {cls}">—</span>'
    if fmt == "inr":
        text = inr(value, dec, sign)
    elif fmt == "pct":
        text = pct(value, dec, sign)
    elif fmt == "x":
        text = num(value, dec) + "×"
    else:
        text = num(value, dec, sign)
    k = f' data-key="{esc(key)}"' if key else ""
    return (f'<span class="ss-num ss-count {cls}" data-v="{float(value)}" data-fmt="{fmt}" '
            f'data-dec="{dec}" data-sign="{1 if sign else 0}"{k}>{text}</span>')


_COUNTUP_JS = """
<script>
(function(){
  var P = window.parent; var D = P.document;
  function fmt(v, dec, kind, sign){
    var neg = v < 0; v = Math.abs(v);
    var s = v.toFixed(dec); var parts = s.split('.'); var ip = parts[0], fp = parts[1];
    if (ip.length > 3) { var tail = ip.slice(-3), head = ip.slice(0,-3), arr=[];
      while (head.length > 2) { arr.unshift(head.slice(-2)); head = head.slice(0,-2); }
      if (head) arr.unshift(head); ip = arr.join(',') + ',' + tail; }
    var out = ip + (dec > 0 ? '.' + fp : '');
    if (kind === 'inr') out = '\\u20B9' + out;
    if (kind === 'pct') out = out + '%';
    if (kind === 'x') out = out + '\\u00D7';
    return (neg ? '\\u2212' : (sign ? '+' : '')) + out;
  }
  var reduce = P.matchMedia && P.matchMedia('(prefers-reduced-motion: reduce)').matches;
  P.__ssPrev = P.__ssPrev || {};
  function animate(el){
    el.setAttribute('data-ss-done','1');
    var v = parseFloat(el.getAttribute('data-v')); if (isNaN(v)) return;
    var dec = parseInt(el.getAttribute('data-dec')||'2'); var kind = el.getAttribute('data-fmt')||'num';
    var sign = el.getAttribute('data-sign') === '1'; var key = el.getAttribute('data-key');
    var from = (key && P.__ssPrev[key] !== undefined) ? P.__ssPrev[key] : 0;
    if (key) P.__ssPrev[key] = v;
    var finalText = fmt(v, dec, kind, sign);
    if (reduce || from === v || D.hidden) { el.textContent = finalText; return; }
    var t0 = null, dur = 300, done = false;
    function finish(){ if (!done) { done = true; el.textContent = finalText; } }
    function step(ts){ if (done) return; if (!t0) t0 = ts; var p = Math.min(1, (ts - t0)/dur); var e = 1 - Math.pow(1-p, 3);
      el.textContent = fmt(from + (v-from)*e, dec, kind, sign); if (p < 1) P.requestAnimationFrame(step); else finish(); }
    P.requestAnimationFrame(step);
    P.setTimeout(finish, dur + 80);  /* rAF is paused in hidden tabs; never leave a half-counted number */
  }
  function scan(){ var els = D.querySelectorAll('.ss-count:not([data-ss-done])'); for (var i=0;i<els.length;i++) animate(els[i]); }
  if (P.__ssObserver) { try { P.__ssObserver.disconnect(); } catch(e){} }
  var pending = false;
  P.__ssObserver = new P.MutationObserver(function(){ if (pending) return; pending = true; P.requestAnimationFrame(function(){ pending=false; scan(); }); });
  P.__ssObserver.observe(D.body, {childList:true, subtree:true});
  scan();
})();
</script>
"""


def countup_runtime() -> None:
    """Installs the count-up animation runtime (once per page render). The 1px
    iframe lives in a keyed container that the CSS takes out of the flow."""
    with st.container(key="ss_runtime"):
        st.iframe(_COUNTUP_JS, height=1)


# =============================================================================
# Market status
# =============================================================================
def market_status() -> dict:
    """NSE hours 09:15–15:30 IST, Monday–Friday (exchange holidays are not modelled)."""
    now_ist = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=5, minutes=30)
    is_weekday = now_ist.weekday() < 5
    m_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    m_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
    is_open = is_weekday and (m_open <= now_ist <= m_close)
    return {
        "open": is_open,
        "time": now_ist.strftime("%H:%M IST"),
        "time_full": now_ist.strftime("%H:%M:%S IST"),
        "label": "Market open" if is_open else "Market closed",
    }


# =============================================================================
# Cached data bundle (keyed on file mtimes so a pipeline run refreshes it)
# =============================================================================
@st.cache_data(ttl=30, show_spinner=False)
def _load_bundle(_sig: float) -> dict:
    prices = dl.load_raw_prices()
    feat = dl.load_engineered_features()
    scores = dl.load_daily_scores()
    news = dl.load_curated_news()
    macro = dl.load_market_sentiment()
    mom = dl.load_sector_momentum()
    preds = dl.load_predictions()
    metrics = dl.load_model_metrics() if os.path.exists(dl.MODEL_METRICS) else {}
    forecast = dl.get_forecast()
    source = dl.detect_data_source(prices)
    serving = dl.load_serving_records()
    return {
        "prices": prices, "feat": feat, "scores": scores, "news": news, "macro": macro,
        "momentum": mom, "preds": preds, "metrics": metrics, "forecast": forecast,
        "source": source, "serving": serving, "metrics_exists": os.path.exists(dl.MODEL_METRICS),
    }


def load_bundle() -> dict:
    return _load_bundle(dl.data_mtime_signature())


def as_of_date(bundle: dict) -> str | None:
    """The last trading day in the feature set (or raw prices)."""
    if not bundle["feat"].empty:
        return str(bundle["feat"]["trade_date"].iloc[-1])
    if not bundle["prices"].empty:
        return str(bundle["prices"]["Date"].iloc[-1])
    return None


# =============================================================================
# Brand chrome: app bar, ticker tape, sidebar blocks, footer
# =============================================================================
def signal_badge_html(signal: str | None, size: str = "") -> str:
    if not signal:
        return f'<span class="ss-badge neutral {size}">No signal</span>'
    cls = signal_class(signal)
    g = {"buy": "▲", "sell": "▼", "hold": "▬"}.get(cls, "")
    return f'<span class="ss-badge {cls} {size}">{g} {esc(signal)}</span>'


def signal_badge(signal: str | None, size: str = "") -> None:
    html(signal_badge_html(signal, size))


def sentiment_chip_html(label: str | None, polarity: float | None = None) -> str:
    lab = str(label or "NEUTRAL").upper()
    cls = "pos" if lab == "POSITIVE" else ("neg" if lab == "NEGATIVE" else "neu")
    p = "" if _is_nan(polarity) else f' <span class="ss-num">{num(polarity, 2, sign=True)}</span>'
    return f'<span class="ss-chip {cls}">{esc(lab.lower())}{p}</span>'


def app_bar(signal: str | None, as_of: str | None) -> None:
    ms = market_status()
    dot = "ss-dot live" if ms["open"] else "ss-dot"
    html(f"""
    <div class="ss-appbar">
      <a class="ss-brand" href="./" target="_self">{T.logo_mark_svg(24)}<span class="ss-wordmark">{T.APP_NAME}</span></a>
      <span class="ss-vdiv"></span>
      <span class="ss-instrument">{T.INSTRUMENT} <span>· {T.EXCHANGE}</span></span>
      <span class="ss-spacer"></span>
      <span class="ss-status"><i class="{dot}"></i>{ms['label']} · <span class="ss-num">{ms['time']}</span></span>
      <span class="ss-vdiv"></span>
      <span class="ss-asof">Data as of <span class="ss-num">{fmt_date(as_of) if as_of else '—'}</span></span>
      <span class="ss-vdiv"></span>
      {signal_badge_html(signal)}
    </div>
    """)


def ticker_tape(items: Sequence[str]) -> None:
    """items are already-safe HTML snippets; the track is doubled for a seamless loop."""
    if not items:
        return
    track = "".join(f'<span class="ss-tape-item">{i}</span>' for i in items)
    html(f'<div class="ss-tape" aria-label="ticker"><div class="ss-tape-track">{track}{track}</div></div>')


def footer() -> None:
    html(f'<div class="ss-footer"><span>{T.APP_NAME} · {T.VERSION} · built on {T.STACK}</span>'
         f'<span>{T.TAGLINE}</span></div>')


def sidebar_kv(rows: Iterable[tuple[str, str]]) -> None:
    html("".join(f'<div class="ss-side-kv"><span>{esc(k)}</span><b>{v}</b></div>' for k, v in rows))


# =============================================================================
# Page structure
# =============================================================================
def page_title(title: str, sub: str | None = None) -> None:
    html(f'<div class="ss-page-title">{esc(title)}</div>' + (f'<div class="ss-page-sub">{sub}</div>' if sub else ""))


def section(title: str, caption: str | None = None) -> None:
    html(f'<div class="ss-section"><h2>{esc(title)}</h2><span>{caption or ""}</span></div>')


def note(text: str, kind: str = "warn") -> None:
    icon = {"warn": "▲", "bad": "✕", "info": "●"}.get(kind, "▲")
    html(f'<div class="ss-note {kind}"><span>{icon}</span><div>{text}</div></div>')


def empty_state(title: str, hint: str, path: str | None = None) -> None:
    p = f'<div style="margin-top:6px"><code>{esc(path)}</code></div>' if path else ""
    html(f'<div class="ss-empty"><b>{esc(title)}</b>{esc(hint)}{p}</div>')


def source_note(text: str) -> None:
    html(f'<div class="ss-src">{text}</div>')


def freshness_tag(path: str, label: str | None = None) -> str:
    """'updated 3 h ago · 4,174 rows' from the file on disk (HTML snippet)."""
    fi = dl.file_info(path, None)
    name = esc(label or fi["name"])
    if not fi["exists"]:
        return f'<span class="ss-chip warn">{name} missing</span>'
    rows = f' · {group_indian(str(fi["rows"]))} rows' if fi["rows"] is not None else ""
    return f'<span class="ss-muted">from <code>{name}</code> · updated {ago(fi["mtime"])}{rows}</span>'


# =============================================================================
# Numbers & tiles
# =============================================================================
def sparkline_svg(values: Sequence[float], w: int = 88, h: int = 30, color: str = T.ACCENT) -> str:
    vals = [float(v) for v in values if not _is_nan(v)]
    if len(vals) < 2:
        return ""
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1.0
    n = len(vals)
    pts = " ".join(f"{i * w / (n - 1):.1f},{h - 2 - (v - lo) / rng * (h - 4):.1f}" for i, v in enumerate(vals))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
            f'<polyline fill="none" stroke="{color}" stroke-width="1.6" stroke-linejoin="round" points="{pts}"/></svg>')


def tile_html(label: str, value_html: str, delta_html: str = "", spark: str = "", sub: str = "",
              label_right: str = "") -> str:
    lr = f'<span class="r">{label_right}</span>' if label_right else ""
    right = f'<div>{spark}</div>' if spark else ""
    d = f'<div class="ss-delta">{delta_html}</div>' if delta_html else ""
    s = f'<div class="ss-sub">{sub}</div>' if sub else ""
    text_cls = " text" if value_html.startswith('<span class="text">') else ""
    return (f'<div class="ss-tile"><div class="ss-label"><span>{esc(label)}</span>{lr}</div>'
            f'<div class="ss-tile-row"><div><div class="ss-val{text_cls}">{value_html}</div>{d}{s}</div>{right}</div></div>')


def metric(label: str, value, fmt: str = "inr", dec: int = 2, delta: float | None = None,
           delta_fmt: str = "pct", delta_text: str | None = None, spark: Sequence[float] | None = None,
           sub: str = "", key: str | None = None, label_right: str = "", help: str | None = None) -> None:
    """A metric tile. value is numeric (counts up) or a ready string."""
    if isinstance(value, str):
        v_html = f'<span class="ss-num">{esc(value)}</span>' if len(value) <= 12 else f'<span class="text">{esc(value)}</span>'
    else:
        v_html = countup_html(value, fmt, dec, key=key)
    d_html = ""
    if delta is not None and not _is_nan(delta):
        tone = tone_for(delta)
        body = pct(delta) if delta_fmt == "pct" else (inr(delta, dec, sign=True) if delta_fmt == "inr" else num(delta, dec, sign=True))
        d_html = f'<span class="{tone}">{glyph_for(delta)} {body}</span>' + (f' <span class="ss-muted">{esc(delta_text)}</span>' if delta_text else "")
    elif delta_text:
        d_html = f'<span class="ss-muted">{esc(delta_text)}</span>'
    html(tile_html(label, v_html, d_html, sparkline_svg(spark) if spark is not None else "", sub, label_right))
    if help:
        st.caption(help)


def hero_number_html(value: float, fmt: str = "inr", dec: int = 2, key: str | None = None, cls: str = "") -> str:
    return f'<div class="ss-hero {cls}">{countup_html(value, fmt, dec, key=key)}</div>'


def range_bar_html(low: float, high: float, value: float, accent: bool = False, dec: int = 2) -> str:
    if any(_is_nan(v) for v in (low, high, value)) or high <= low:
        return '<div class="ss-sub">range unavailable</div>'
    pos = max(0.0, min(100.0, (value - low) / (high - low) * 100.0))
    return (f'<div class="ss-rbar {"accent" if accent else ""}"><i style="left:{pos:.1f}%"></i></div>'
            f'<div class="ss-rlabels"><span>{num(low, dec)}</span><span>{num(high, dec)}</span></div>')


def confidence_ring_html(pct_value: float, color: str = T.ACCENT) -> str:
    if _is_nan(pct_value):
        return '<div class="ss-ring"><b>—</b></div>'
    r = 27
    c = 2 * math.pi * r
    off = c * (1 - max(0.0, min(100.0, float(pct_value))) / 100.0)
    return (f'<div class="ss-ring"><svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
            f'<circle cx="32" cy="32" r="{r}" stroke="{T.BORDER}" stroke-width="6" fill="none"/>'
            f'<circle class="v" cx="32" cy="32" r="{r}" stroke="{color}" stroke-width="6" fill="none" '
            f'stroke-dasharray="{c:.1f}" stroke-dashoffset="{off:.1f}" stroke-linecap="round"/></svg>'
            f'<b>{num(pct_value, 0)}%</b></div>')


def gauge_svg(value: float, width: int = 170) -> str:
    """Semicircle composite gauge with SELL / HOLD / BUY / STRONG BUY bands."""
    if _is_nan(value):
        return '<div class="ss-sub">score unavailable</div>'
    v = max(0.0, min(100.0, float(value)))
    cx, cy, r = 85, 82, 66
    def pt(a_deg):
        a = math.radians(180 - a_deg)
        return cx + r * math.cos(a), cy - r * math.sin(a)
    def arc(a0, a1, color, opacity=1.0):
        x0, y0 = pt(a0 * 1.8)
        x1, y1 = pt(a1 * 1.8)
        large = 1 if (a1 - a0) * 1.8 > 180 else 0
        return (f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}" stroke="{color}" '
                f'stroke-width="10" fill="none" opacity="{opacity}"/>')
    bands = (arc(0, SELL_MAX, T.DOWN, .6) + arc(SELL_MAX, BUY_MIN, T.WARN, .6)
             + arc(BUY_MIN, STRONG_BUY_MIN, T.UP, .55) + arc(STRONG_BUY_MIN, 100, T.UP, .95))
    nx, ny = pt(v * 1.8)
    ticks = "".join(
        f'<text x="{pt(t * 1.8)[0]:.0f}" y="{pt(t * 1.8)[1] + (14 if t in (0, 100) else -9):.0f}" text-anchor="middle" '
        f'font-family="{T.FONT_MONO}" font-size="9" fill="{T.MUTED}">{t:.0f}</text>'
        for t in (0, SELL_MAX, BUY_MIN, STRONG_BUY_MIN, 100))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{int(width * 0.56)}" viewBox="0 0 170 95" aria-label="composite gauge">'
            f'{bands}{ticks}<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{T.TEXT}" stroke-width="2.5" '
            f'stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="4" fill="{T.TEXT}"/>'
            f'<text x="{cx}" y="{cy - 14}" text-anchor="middle" font-family="{T.FONT_MONO}" font-weight="700" '
            f'font-size="17" fill="{T.TEXT}">{v:.1f}</text></svg>')


def brief_list(sentences: Sequence[str]) -> None:
    html('<ul class="ss-brief">' + "".join(f'<li><i></i><span>{s}</span></li>' for s in sentences) + "</ul>")


def card_open(cls: str = "") -> None:
    html(f'<div class="ss-card {cls}">')


# =============================================================================
# Charts (shared template)
# =============================================================================
def chart(fig: go.Figure, key: str | None = None, height: int | None = None) -> None:
    if height:
        fig.update_layout(height=height)
    st.plotly_chart(fig, width="stretch", theme=None, config=T.PLOTLY_CONFIG, key=key)


def fig_fan(dates: Sequence[str], closes: Sequence[float], target_date: str, pred: float,
            low: float, high: float, height: int = 220) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(dates), y=list(closes), mode="lines", name="Close",
                             line=dict(color=T.TEXT2, width=1.8), hovertemplate="%{x}<br>₹%{y:,.2f}<extra></extra>"))
    last_x, last_y = dates[-1], closes[-1]
    fig.add_trace(go.Scatter(x=[last_x, target_date, target_date, last_x], y=[last_y, high, low, last_y],
                             fill="toself", fillcolor="rgba(25,211,197,0.14)", line=dict(width=0),
                             hoverinfo="skip", showlegend=True, name="±MAE band"))
    fig.add_trace(go.Scatter(x=[last_x, target_date], y=[last_y, pred], mode="lines+markers", name="Forecast",
                             line=dict(color=T.ACCENT, width=2, dash="dash"), marker=dict(size=[0, 9], color=T.ACCENT),
                             hovertemplate="%{x}<br>₹%{y:,.2f}<extra>forecast</extra>"))
    for y, txt, col in ((high, inr(high, 0), T.TEXT2), (pred, inr(pred, 0), T.ACCENT), (low, inr(low, 0), T.TEXT2)):
        fig.add_annotation(x=target_date, y=y, text=txt, showarrow=False, xanchor="left", xshift=8,
                           font=dict(family=T.FONT_STACK_MONO, size=10, color=col))
    fig.update_layout(height=height, margin=dict(l=4, r=70, t=10, b=4), showlegend=True,
                      yaxis=dict(tickprefix="₹", tickformat=",.0f", side="left"), xaxis=dict(showgrid=False))
    return fig


def fig_waterfall(t: float, f: float, n: float, r: float, height: int = 230) -> go.Figure:
    w = COMPOSITE_WEIGHTS
    contrib = [w["T"] * t, w["F"] * f, w["N"] * n, w["R"] * r]
    total = sum(contrib)
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * 4 + ["total"],
        x=["0.40 · T", "0.20 · F", "0.25 · N", "0.15 · R", "= S"],
        y=contrib + [total],
        text=[f"{c:.1f}" for c in contrib] + [f"{total:.1f}"],
        textposition="outside",
        textfont=dict(family=T.FONT_STACK_MONO, size=11, color=T.TEXT),
        connector=dict(line=dict(color=T.BORDER2, width=1, dash="dot")),
        increasing=dict(marker=dict(color=T.ACCENT)),
        decreasing=dict(marker=dict(color=T.DOWN)),
        totals=dict(marker=dict(color=T.TEXT)),
        hovertemplate="%{x}: %{y:.2f}<extra></extra>",
    ))
    fig.update_layout(height=height, margin=dict(l=4, r=4, t=10, b=4), showlegend=False,
                      yaxis=dict(range=[0, max(100, total * 1.15)], showgrid=True), xaxis=dict(showgrid=False),
                      hovermode="x")
    fig.add_hline(y=BUY_MIN, line=dict(color=T.UP, width=1, dash="dot"),
                  annotation_text=f"BUY ≥{BUY_MIN:.0f}", annotation_position="top left",
                  annotation_font=dict(size=10, color=T.UP))
    fig.add_hline(y=SELL_MAX, line=dict(color=T.DOWN, width=1, dash="dot"),
                  annotation_text=f"SELL ≤{SELL_MAX:.0f}", annotation_position="bottom left",
                  annotation_font=dict(size=10, color=T.DOWN))
    return fig


def fig_calendar_heatmap(df: pd.DataFrame, date_col: str = "trade_date", ret_col: str = "daily_return",
                         months: int = 12, height: int = 190) -> go.Figure:
    d = df[[date_col, ret_col]].dropna().copy()
    d[date_col] = pd.to_datetime(d[date_col])
    end = d[date_col].max()
    d = d[d[date_col] > end - pd.DateOffset(months=months)]
    start = d[date_col].min() - pd.Timedelta(days=int(d[date_col].min().weekday()))
    d["week"] = ((d[date_col] - start).dt.days // 7).astype(int)
    d["dow"] = d[date_col].dt.weekday
    z = np.full((5, int(d["week"].max()) + 1), np.nan)
    txt = np.full(z.shape, "", dtype=object)
    for _, row in d.iterrows():
        z[row["dow"], row["week"]] = row[ret_col]
        txt[row["dow"], row["week"]] = f"{row[date_col].strftime('%d %b %Y')}<br>{pct(row[ret_col])}"
    amax = float(np.nanmax(np.abs(z))) if np.isfinite(np.nanmax(np.abs(z))) else 1.0
    firsts = d.groupby(d[date_col].dt.to_period("M"))["week"].min()
    labels = [p.strftime("%b") for p in firsts.index]
    fig = go.Figure(go.Heatmap(
        z=z, x=list(range(z.shape[1])), y=["Mon", "Tue", "Wed", "Thu", "Fri"], text=txt,
        hovertemplate="%{text}<extra></extra>", zmid=0, zmin=-amax, zmax=amax,
        colorscale=[[0, T.DOWN], [0.5, T.SURFACE2], [1, T.UP]], xgap=2, ygap=2,
        colorbar=dict(title=dict(text="%", font=dict(size=10)), thickness=8, len=0.9, tickfont=dict(size=9)),
    ))
    fig.update_layout(height=height, margin=dict(l=4, r=4, t=8, b=4), hovermode="closest",
                      xaxis=dict(tickmode="array", tickvals=list(firsts.values), ticktext=labels, showgrid=False),
                      yaxis=dict(autorange="reversed", showgrid=False, side="left"))
    return fig


def fig_importances(importances: dict, height: int = 320) -> go.Figure:
    df = pd.DataFrame(list(importances.items()), columns=["feature", "importance"]).sort_values("importance")
    fig = go.Figure(go.Bar(
        x=df["importance"] * 100.0, y=df["feature"], orientation="h", marker=dict(color=T.ACCENT),
        text=[f"{v * 100:.1f}%" for v in df["importance"]], textposition="outside",
        textfont=dict(family=T.FONT_STACK_MONO, size=10, color=T.TEXT2),
        hovertemplate="%{y}: %{x:.2f}%<extra></extra>",
    ))
    fig.update_layout(height=height, margin=dict(l=8, r=48, t=8, b=4), hovermode="closest",
                      xaxis=dict(title="Relative importance (%)", range=[0, float(df["importance"].max()) * 118], showgrid=True),
                      yaxis=dict(showgrid=False, side="left", tickfont=dict(size=11), automargin=True))
    return fig


# =============================================================================
# Tables & filters
# =============================================================================
def csv_download(df: pd.DataFrame, name: str, key: str | None = None) -> None:
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"{name}.csv",
                       mime="text/csv", key=key or f"dl_{name}", type="tertiary", icon=":material/download:")


def table(df: pd.DataFrame, name: str, column_config: dict | None = None, height: int | None = None,
          hide_index: bool = True, download: bool = True, key: str | None = None) -> None:
    if df is None or df.empty:
        empty_state("No rows", "Nothing to show for this view.")
        return
    cfg = dict(column_config or {})
    for c in df.columns:
        if c not in cfg and pd.api.types.is_numeric_dtype(df[c]):
            cfg[c] = st.column_config.NumberColumn(c, format="%.2f" if pd.api.types.is_float_dtype(df[c]) else "%d")
    st.dataframe(df, width="stretch", hide_index=hide_index, column_config=cfg, height=height or "auto", key=key)
    if download:
        csv_download(df, name, key=f"dl_{name}_{key or ''}")


def date_range_filter(df: pd.DataFrame, col: str, key: str, default_days: int | None = 180,
                      label: str = "Date range") -> pd.DataFrame:
    """A from–to date picker bound to the data's own range. Returns the filtered frame."""
    if df.empty or col not in df.columns:
        return df
    dates = pd.to_datetime(df[col])
    dmin, dmax = dates.min().date(), dates.max().date()
    start_default = max(dmin, (dates.max() - pd.Timedelta(days=default_days)).date()) if default_days else dmin
    picked = st.date_input(label, value=(start_default, dmax), min_value=dmin, max_value=dmax, key=key, format="DD/MM/YYYY")
    if isinstance(picked, (tuple, list)):
        if len(picked) == 2:
            a, b = picked
        elif len(picked) == 1:
            a, b = picked[0], dmax
        else:
            a, b = dmin, dmax
    else:
        a, b = picked, dmax
    mask = (dates.dt.date >= a) & (dates.dt.date <= b)
    return df.loc[mask]


# =============================================================================
# Domain helpers: brief sentences, technical breakdown, stage strip, news cards
# =============================================================================
def vwap_streak(feat: pd.DataFrame) -> tuple[str, int]:
    """('below'|'above', n) consecutive sessions the close has been on one side of VWAP."""
    if feat.empty:
        return ("—", 0)
    side = None
    n = 0
    for c, v in zip(feat["close_price"].iloc[::-1], feat["vwap"].iloc[::-1]):
        s = "below" if c < v else "above"
        if side is None:
            side = s
        if s != side:
            break
        n += 1
    return (side or "—", n)


def ordinal(n: int) -> str:
    return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def technical_breakdown(row: pd.Series) -> list[dict]:
    """Mirrors compute_technical_score() in spark_score_engine.py: each rule's state and sub-score."""
    close, ema20, ema50, vwap = float(row["close_price"]), float(row["ema_20"]), float(row["ema_50"]), float(row["vwap"])
    rsi, hist, bb, vr = float(row["rsi_14"]), float(row["macd_hist"]), float(row["bb_pos"]), float(row["volume_ratio"])
    s_ema = 100.0 if ema20 >= ema50 else 20.0
    s_vwap = 100.0 if close >= vwap else 25.0
    if 45.0 <= rsi <= 65.0:
        s_rsi, rsi_state = 90.0, "Healthy momentum (45–65)"
    elif rsi > 70.0:
        s_rsi, rsi_state = 35.0, "Overbought (>70)"
    elif rsi < 30.0:
        s_rsi, rsi_state = 65.0, "Oversold (<30)"
    else:
        s_rsi, rsi_state = 50.0, "Neutral"
    s_macd = 90.0 if hist > 0 else 30.0
    s_bb = float(np.clip(bb * 100.0, 10.0, 95.0))
    s_vol = 90.0 if vr >= 1.25 else 50.0
    bb_state = "Near upper band" if bb > 0.8 else ("Near lower band" if bb < 0.2 else "Mid-range")
    return [
        {"indicator": "RSI (14)", "value": f"{rsi:.1f}", "state": rsi_state, "sub": s_rsi, "raw": rsi},
        {"indicator": "MACD histogram", "value": num(hist, 2, sign=True), "state": "Bullish (above signal)" if hist > 0 else "Bearish (below signal)", "sub": s_macd, "raw": hist},
        {"indicator": "EMA 20 vs 50", "value": f"{num(ema20, 0)} vs {num(ema50, 0)}", "state": "Short-term uptrend" if ema20 >= ema50 else "Short-term downtrend", "sub": s_ema, "raw": ema20 - ema50},
        {"indicator": "Close vs VWAP", "value": pct((close - vwap) / vwap * 100.0), "state": "Above VWAP (support)" if close >= vwap else "Below VWAP (resistance)", "sub": s_vwap, "raw": close - vwap},
        {"indicator": "Bollinger position", "value": f"{bb:.2f}", "state": bb_state, "sub": s_bb, "raw": bb},
        {"indicator": "Volume vs 20-day", "value": f"{vr:.2f}×", "state": "Surge (≥1.25×)" if vr >= 1.25 else "Normal", "sub": s_vol, "raw": vr},
    ]


def brief_sentences(feat: pd.DataFrame, scores: pd.DataFrame, forecast: dict | None) -> list[str]:
    """3–4 plain-English sentences built from rules over the latest data (no LLM)."""
    out: list[str] = []
    if feat.empty:
        return ["No feature data available, so there is nothing to brief."]
    last = feat.iloc[-1]
    side, n = vwap_streak(feat)
    if n >= 2:
        out.append(f"Price closed <b>{side} VWAP</b> for the <span class='ss-num'>{ordinal(n)}</span> straight session.")
    else:
        out.append(f"Price closed <b>{side} VWAP</b> today, flipping sides after the previous session.")
    rsi = float(last["rsi_14"])
    if rsi < 30:
        out.append(f"RSI <span class='ss-num'>{rsi:.1f}</span> is <b>oversold</b> (below 30); the score credits a rebound setup.")
    elif rsi > 70:
        out.append(f"RSI <span class='ss-num'>{rsi:.1f}</span> is <b>overbought</b> (above 70); the score applies caution.")
    elif 45 <= rsi <= 65:
        out.append(f"RSI <span class='ss-num'>{rsi:.1f}</span> sits in the healthy 45–65 momentum zone.")
    else:
        out.append(f"RSI <span class='ss-num'>{rsi:.1f}</span> is neutral, neither stretched nor oversold.")
    if not scores.empty:
        s = float(scores.iloc[-1]["composite_score"])
        band = band_label(s)
        nxt = ""
        if s < BUY_MIN:
            nxt = f"; BUY needs <span class='ss-num'>{BUY_MIN:.0f}</span>"
        elif s < STRONG_BUY_MIN:
            nxt = f"; STRONG BUY needs <span class='ss-num'>{STRONG_BUY_MIN:.0f}</span>"
        out.append(f"Composite <span class='ss-num'>{s:.1f}</span> sits in the <b>{band}</b>{nxt}.")
    ema_txt = "below" if float(last["ema_20"]) < float(last["ema_50"]) else "above"
    vr = float(last["volume_ratio"])
    out.append(f"EMA 20 is <b>{ema_txt}</b> EMA 50 and volume ran <span class='ss-num'>{vr:.2f}×</span> its 20-day average"
               + (" (a surge the score rewards)." if vr >= 1.25 else "."))
    if forecast and forecast.get("direction"):
        pass  # direction is already shown next to the forecast; keep the brief to four lines
    return out[:4]


def stage_strip(stages: list[dict]) -> None:
    """Compact pipeline health strip: dot colour from freshness, rows and age from disk."""
    pills = []
    for s in stages:
        if not s["exists"]:
            cls, txt = "bad", "missing"
        else:
            age_h = (dt.datetime.now() - s["mtime"]).total_seconds() / 3600 if s["mtime"] else 1e9
            cls = "ok" if age_h < 24 else "warn"
            rows = f"{group_indian(str(s['rows']))} rows · " if s["rows"] is not None else ""
            txt = f"{rows}{ago(s['mtime'])}"
        pills.append(f'<span class="ss-stage"><i class="ss-dot {cls}"></i><b>{esc(s["stage"])}</b> {txt}</span>')
    html(f'<div class="ss-strip">{"".join(pills)}</div>')


def news_card_html(row: pd.Series, summary_chars: int = 110) -> str:
    pol = row.get("polarity_score", np.nan)
    try:
        pol = float(pol)
    except (TypeError, ValueError):
        pol = np.nan
    width = 0.0 if _is_nan(pol) else min(50.0, abs(pol) * 50.0)
    bar = f'<div class="ss-pbar"><i class="{"neg" if (not _is_nan(pol) and pol < 0) else ""}" style="width:{width:.1f}%"></i></div>'
    link = row.get("link", "")
    title = esc(row.get("title", ""))
    t = f'<a href="{esc(link)}" target="_blank" rel="noopener">{title}</a>' if isinstance(link, str) and link.startswith("http") else title
    summary = str(row.get("summary", "") or "")
    sm = esc(summary[:summary_chars] + ("…" if len(summary) > summary_chars else ""))
    return (f'<div class="ss-ncard"><div class="meta"><span>{esc(row.get("source", "News"))}</span>'
            f'<span class="ss-num">{fmt_date(row.get("trade_date"))}</span></div><div class="t">{t}</div>'
            f'<div class="sm">{sm}</div>{bar}<div>{sentiment_chip_html(row.get("sentiment_label"), pol)}</div></div>')


def news_cards(df: pd.DataFrame, cols: int = 5) -> None:
    if df.empty:
        empty_state("No news rows", "The curated feed is empty.", dl.RAW_NEWS)
        return
    columns = st.columns(min(cols, len(df)))
    for i, (_, row) in enumerate(df.iterrows()):
        with columns[i % len(columns)]:
            html(news_card_html(row))


def flow_diagram(nodes: Sequence[tuple[str, str, str]]) -> None:
    """nodes: (kicker, title, detail)."""
    parts = []
    for i, (k, v, d) in enumerate(nodes):
        if i:
            parts.append('<div class="arrow">›</div>')
        parts.append(f'<div class="node"><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div><div class="d">{esc(d)}</div></div>')
    html(f'<div class="ss-flow">{"".join(parts)}</div>')


def glossary() -> None:
    """Popover explaining the scores, the model error and the signal thresholds."""
    with st.popover("Glossary", icon=":material/menu_book:", width="stretch"):
        st.markdown(f"""
**T · Technical score (0–100)** — six rules on EMA 20/50, close vs VWAP, RSI 14, MACD histogram, Bollinger position and volume surge, averaged.

**F · Fundamental score** — fixed valuation baseline (P/E, ROE, debt/equity, growth) for Reliance; constant in this pipeline.

**N · News score** — TextBlob polarity of matched headlines scaled to 0–100 with a 3-session decay; 50 means no news matched.

**R · Real-time score** — intraday return and volume ratio from the streaming stage.

**S · Composite** — `S = 0.40·T + 0.20·F + 0.25·N + 0.15·R`.

**Signal thresholds** — STRONG BUY: S ≥ {STRONG_BUY_MIN:.0f} and predicted return > 0 · BUY: S ≥ {BUY_MIN:.0f} and return > 0 · SELL: S ≤ {SELL_MAX:.0f} or return < {SELL_RET:.0f}% · otherwise HOLD.

**MAE** — mean absolute error of the model on the held-out test window, in rupees. The forecast band is ±MAE.

**Naive baseline** — "tomorrow's close = today's close". A useful model must beat it.
""")
