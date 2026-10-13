"""
theme.py — Stock sight design tokens, CSS and the shared Plotly template
=======================================================================
Every colour, font and size used by the dashboard is defined here once.
Pages must not contain inline style strings; they use components.py helpers,
which read these tokens. The same values are mirrored in .streamlit/config.toml.
"""

from __future__ import annotations

import os

import plotly.graph_objects as go
import plotly.io as pio

# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------
APP_NAME = "Stock sight"
TAGLINE = "Market foresight for Reliance Industries"
INSTRUMENT = "RELIANCE"
EXCHANGE = "NSE"
VERSION = "v1"
STACK = "Hadoop · Spark · Hive · HBase · Kafka"

# ---------------------------------------------------------------------------
# Colour tokens (dark-first). Contrast ratios are documented in docs/DESIGN_BRIEF.md
# ---------------------------------------------------------------------------
INK = "#0A0E14"
SURFACE1 = "#111722"
SURFACE2 = "#182130"
BORDER = "#232D3F"
BORDER2 = "#2E3A4F"
TEXT = "#E8EDF5"
TEXT2 = "#9AA6B8"
MUTED = "#7F8B9E"
ACCENT = "#19D3C5"
ACCENT_INK = "#06211F"
UP = "#22C55E"
DOWN = "#F2555A"
WARN = "#F5A524"
NEUTRAL = "#9AA6B8"
VIOLET = "#A78BFA"
BLUE = "#60A5FA"

SIGNAL_COLORS = {
    "STRONG BUY": UP,
    "BUY": UP,
    "HOLD": WARN,
    "SELL": DOWN,
}
DIRECTION_GLYPH = {"UP": "▲", "DOWN": "▼", "FLAT": "▬"}

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONT_DISPLAY = "Space Grotesk"
FONT_UI = "Inter"
FONT_MONO = "JetBrains Mono"
FONT_STACK_DISPLAY = f"'{FONT_DISPLAY}', '{FONT_UI}', sans-serif"
FONT_STACK_UI = f"'{FONT_UI}', system-ui, -apple-system, sans-serif"
FONT_STACK_MONO = f"'{FONT_MONO}', ui-monospace, Menlo, monospace"
GOOGLE_FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700"
    "&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600;700&display=swap"
)

# Five sizes only
SIZE_XL = "2.6rem"
SIZE_L = "1.375rem"
SIZE_M = "0.9375rem"
SIZE_S = "0.8125rem"
SIZE_XS = "0.6875rem"

# ---------------------------------------------------------------------------
# Logo mark: an eye whose lower lid is a rising price line
# ---------------------------------------------------------------------------
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
MARK_SVG_PATH = os.path.join(ASSETS_DIR, "stocksight-mark.svg")
WORDMARK_SVG_PATH = os.path.join(ASSETS_DIR, "stocksight-wordmark.svg")


def logo_mark_svg(size: int = 24, color: str = ACCENT) -> str:
    """Inline SVG of the Stock sight mark."""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 32 32" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Stock sight">'
        f'<path d="M3 17C8 8 24 8 29 17" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>'
        f'<path d="M3 17L9 23L14 19L19 25L24 20L29 17" stroke="{color}" stroke-width="2.4" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        f'<circle cx="16" cy="16.5" r="3.6" fill="{color}"/></svg>'
    )


def wordmark_svg() -> str:
    """Standalone SVG with mark + wordmark, used by st.logo in the sidebar."""
    return (
        '<svg width="190" height="36" viewBox="0 0 190 36" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<g transform="translate(2,2)">{logo_mark_svg(32)[logo_mark_svg(32).find(">") + 1:-6]}</g>'
        f'<text x="44" y="25" font-family="{FONT_DISPLAY}, Inter, sans-serif" font-size="19" '
        f'font-weight="600" letter-spacing="-0.4" fill="{TEXT}">Stock sight</text></svg>'
    )


def ensure_assets() -> None:
    """Writes the SVG favicon and sidebar wordmark to assets/ if they are missing."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    if not os.path.exists(MARK_SVG_PATH):
        with open(MARK_SVG_PATH, "w", encoding="utf-8") as f:
            f.write(logo_mark_svg(32))
    if not os.path.exists(WORDMARK_SVG_PATH):
        with open(WORDMARK_SVG_PATH, "w", encoding="utf-8") as f:
            f.write(wordmark_svg())


# ---------------------------------------------------------------------------
# Plotly template
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE = "stocksight"


def register_plotly_template() -> None:
    """Registers and activates the shared Plotly template."""
    if PLOTLY_TEMPLATE in pio.templates:
        pio.templates.default = PLOTLY_TEMPLATE
        return
    axis_common = dict(
        gridcolor=BORDER,
        linecolor=BORDER,
        zeroline=False,
        showline=False,
        ticks="",
        tickfont=dict(family=FONT_STACK_MONO, size=11, color=TEXT2),
        title=dict(font=dict(size=11, color=MUTED)),
    )
    t = go.layout.Template()
    t.layout = go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_STACK_UI, size=12, color=TEXT2),
        title=dict(font=dict(family=FONT_STACK_DISPLAY, size=15, color=TEXT), x=0, xanchor="left"),
        colorway=[ACCENT, BLUE, VIOLET, WARN, UP, DOWN],
        xaxis=dict(
            **axis_common,
            showspikes=True,
            spikecolor=BORDER2,
            spikethickness=1,
            spikedash="dot",
            spikemode="across",
            spikesnap="cursor",
        ),
        yaxis=dict(**axis_common, side="right"),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=SURFACE2,
            bordercolor=BORDER2,
            font=dict(family=FONT_STACK_MONO, size=12, color=TEXT),
            align="left",
        ),
        legend=dict(
            orientation="h",
            y=1.02,
            yanchor="bottom",
            x=0,
            xanchor="left",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=TEXT2),
            itemsizing="constant",
        ),
        margin=dict(l=8, r=8, t=28, b=8),
        transition=dict(duration=250, easing="cubic-in-out"),
        dragmode="pan",
    )
    t.data.candlestick = [
        go.Candlestick(
            increasing=dict(line=dict(color=UP, width=1), fillcolor=UP),
            decreasing=dict(line=dict(color=DOWN, width=1), fillcolor=DOWN),
            whiskerwidth=0.4,
        )
    ]
    t.data.bar = [go.Bar(marker=dict(line=dict(width=0)))]
    t.data.scatter = [go.Scatter(line=dict(width=1.8))]
    pio.templates[PLOTLY_TEMPLATE] = t
    pio.templates.default = PLOTLY_TEMPLATE


PLOTLY_CONFIG = {
    "displaylogo": False,
    "displayModeBar": False,
    "scrollZoom": False,
    "responsive": True,
}


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
def build_css() -> str:
    return f"""
<style>
@import url('{GOOGLE_FONTS_URL}');
:root {{
  --ss-ink:{INK}; --ss-s1:{SURFACE1}; --ss-s2:{SURFACE2}; --ss-border:{BORDER}; --ss-border2:{BORDER2};
  --ss-text:{TEXT}; --ss-text2:{TEXT2}; --ss-muted:{MUTED}; --ss-accent:{ACCENT}; --ss-accent-ink:{ACCENT_INK};
  --ss-up:{UP}; --ss-down:{DOWN}; --ss-warn:{WARN}; --ss-neutral:{NEUTRAL}; --ss-violet:{VIOLET}; --ss-blue:{BLUE};
  --ss-display:{FONT_STACK_DISPLAY}; --ss-ui:{FONT_STACK_UI}; --ss-mono:{FONT_STACK_MONO};
  --ss-xl:{SIZE_XL}; --ss-l:{SIZE_L}; --ss-m:{SIZE_M}; --ss-s:{SIZE_S}; --ss-xs:{SIZE_XS};
  --ss-ease:cubic-bezier(.2,.7,.2,1); --ss-radius:12px;
}}

/* ---------- base ---------- */
html, body, .stApp, [data-testid="stAppViewContainer"] {{ font-family: var(--ss-ui); }}
.stApp {{ background: var(--ss-ink); color: var(--ss-text); }}
[data-testid="stAppViewContainer"] .block-container {{ padding: 0 1.75rem 2.5rem 1.75rem; max-width: 1520px; }}
[data-testid="stHeader"] {{ background: transparent; height: 0; }}
[data-testid="stHeader"] > * {{ pointer-events: auto; }}
[data-testid="stToolbar"] {{ top: 0.6rem; right: 0.75rem; }}
[data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] {{ top: 0.8rem; left: 0.6rem; z-index: 1000; }}
h1, h2, h3 {{ font-family: var(--ss-display) !important; letter-spacing: -0.01em; color: var(--ss-text); }}
h1 {{ font-size: var(--ss-l) !important; font-weight: 600 !important; padding: 0 !important; margin: 0 0 0.25rem 0 !important; }}
h2 {{ font-size: var(--ss-l) !important; font-weight: 600 !important; }}
h3 {{ font-size: var(--ss-m) !important; font-weight: 600 !important; }}
code, kbd, pre, .stCode, [data-testid="stMetricValue"] {{ font-family: var(--ss-mono) !important; font-variant-numeric: tabular-nums; }}
a {{ color: var(--ss-accent); }}
hr {{ border-color: var(--ss-border) !important; margin: 1.25rem 0 !important; }}
.ss-num {{ font-family: var(--ss-mono); font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1; }}
.ss-up {{ color: var(--ss-up); }} .ss-down {{ color: var(--ss-down); }} .ss-warn {{ color: var(--ss-warn); }}
.ss-accent {{ color: var(--ss-accent); }} .ss-muted {{ color: var(--ss-muted); }} .ss-text2 {{ color: var(--ss-text2); }}
.ss-neutral {{ color: var(--ss-neutral); }}

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] {{ background: var(--ss-s1); border-right: 1px solid var(--ss-border); }}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {{ border-radius: 8px; font-size: var(--ss-s); font-weight: 500; color: var(--ss-text2); }}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {{
  background: var(--ss-s2); color: var(--ss-text); box-shadow: inset 3px 0 0 var(--ss-accent); }}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span {{ color: inherit; }}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {{ background: var(--ss-s2); }}
.ss-side-kv {{ display:flex; justify-content:space-between; gap:12px; font-size: var(--ss-s); color: var(--ss-text2); padding: 5px 0; border-bottom: 1px solid var(--ss-border); }}
.ss-side-kv b {{ color: var(--ss-text); font-weight: 500; text-align:right; }}
.ss-side-kv:last-child {{ border-bottom: 0; }}

/* ---------- app bar ---------- */
.ss-appbar {{ position: sticky; top: 0; z-index: 60; display:flex; align-items:center; gap:14px; height:56px; margin: 0 -1.75rem; padding: 0 3rem 0 1.75rem; background: rgba(10,14,20,.94); border-bottom:1px solid var(--ss-border); }}
.stApp:has([data-testid="stSidebarCollapsedControl"]) .ss-appbar,
.stApp:has([data-testid="stExpandSidebarButton"]) .ss-appbar {{ padding-left: 3.4rem; }}
.ss-brand, .ss-brand:hover, .ss-brand:visited {{ display:flex; align-items:center; gap:9px; color: var(--ss-text) !important; text-decoration:none !important; }}
.ss-wordmark {{ font-family: var(--ss-display); font-weight:600; font-size:1.125rem; letter-spacing:-.02em; color: var(--ss-text); }}
.ss-vdiv {{ width:1px; height:22px; background: var(--ss-border2); flex:none; }}
.ss-instrument {{ font-family: var(--ss-mono); font-size: var(--ss-s); font-weight:600; letter-spacing:.04em; color: var(--ss-text); white-space:nowrap; }}
.ss-instrument span {{ color: var(--ss-muted); font-weight:500; }}
.ss-spacer {{ flex:1; }}
.ss-status {{ display:inline-flex; align-items:center; gap:7px; font-size: var(--ss-s); color: var(--ss-text2); white-space:nowrap; }}
.ss-asof {{ font-size: var(--ss-s); color: var(--ss-muted); white-space:nowrap; }}
.ss-dot {{ width:8px; height:8px; border-radius:50%; background: var(--ss-neutral); flex:none; }}
.ss-dot.live {{ background: var(--ss-up); animation: ss-pulse 1.6s ease-out infinite; }}
.ss-dot.ok {{ background: var(--ss-up); }} .ss-dot.warn {{ background: var(--ss-warn); }} .ss-dot.bad {{ background: var(--ss-down); }}
@keyframes ss-pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(34,197,94,.55); }} 100% {{ box-shadow: 0 0 0 8px rgba(34,197,94,0); }} }}

/* ---------- ticker tape ---------- */
.ss-tape {{ margin: 0 -1.75rem 1.25rem; border-bottom:1px solid var(--ss-border); background: var(--ss-s1); overflow:hidden; height:34px; display:flex; align-items:center; }}
.ss-tape-track {{ display:flex; gap:40px; white-space:nowrap; animation: ss-tape 48s linear infinite; padding-left: 1.75rem; width:max-content; }}
.ss-tape:hover .ss-tape-track {{ animation-play-state: paused; }}
@keyframes ss-tape {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-50%); }} }}
.ss-tape-item {{ display:inline-flex; align-items:center; gap:8px; font-size: var(--ss-s); color: var(--ss-text2); }}
.ss-tape-item b {{ color: var(--ss-text); font-weight:600; }}

/* ---------- badges & chips ---------- */
.ss-badge {{ display:inline-flex; align-items:center; gap:6px; padding:3px 10px; border-radius:6px; font-family: var(--ss-ui); font-size: var(--ss-xs); font-weight:600; letter-spacing:.08em; text-transform:uppercase; border:1px solid; white-space:nowrap;
  transition: background .25s var(--ss-ease), color .25s var(--ss-ease), border-color .25s var(--ss-ease); }}
.ss-badge.buy {{ color: var(--ss-up); border-color: rgba(34,197,94,.45); background: rgba(34,197,94,.10); }}
.ss-badge.hold {{ color: var(--ss-warn); border-color: rgba(245,165,36,.45); background: rgba(245,165,36,.10); }}
.ss-badge.sell {{ color: var(--ss-down); border-color: rgba(242,85,90,.45); background: rgba(242,85,90,.10); }}
.ss-badge.neutral {{ color: var(--ss-neutral); border-color: var(--ss-border2); background: var(--ss-s2); }}
.ss-badge.lg {{ font-size: var(--ss-s); padding:6px 14px; border-radius:8px; }}
.ss-badge.xl {{ font-size: var(--ss-m); padding:8px 18px; border-radius:10px; }}
.ss-chip {{ display:inline-flex; align-items:center; gap:5px; padding:1px 7px; border-radius:4px; font-size: var(--ss-xs); font-weight:600; letter-spacing:.06em; text-transform:uppercase; border:1px solid; white-space:nowrap; }}
.ss-chip.pos {{ color: var(--ss-up); border-color: rgba(34,197,94,.4); }}
.ss-chip.neg {{ color: var(--ss-down); border-color: rgba(242,85,90,.4); }}
.ss-chip.neu {{ color: var(--ss-neutral); border-color: var(--ss-border2); }}
.ss-chip.warn {{ color: var(--ss-warn); border-color: rgba(245,165,36,.4); }}
.ss-chip.accent {{ color: var(--ss-accent); border-color: rgba(25,211,197,.4); }}

/* ---------- labels, numbers, cards ---------- */
.ss-label {{ font-family: var(--ss-ui); font-size: var(--ss-xs); font-weight:600; letter-spacing:.08em; text-transform:uppercase; color: var(--ss-text2); margin-bottom:6px; display:flex; justify-content:space-between; gap:10px; }}
.ss-label .r {{ font-weight:500; letter-spacing:0; text-transform:none; color: var(--ss-muted); }}
.ss-hero {{ font-family: var(--ss-mono); font-size: var(--ss-xl); font-weight:700; line-height:1; letter-spacing:-.03em; color: var(--ss-text); font-variant-numeric: tabular-nums; white-space:nowrap; }}
.ss-val {{ font-family: var(--ss-mono); font-size: var(--ss-l); font-weight:600; line-height:1.1; color: var(--ss-text); font-variant-numeric: tabular-nums; }}
.ss-sub {{ font-size: var(--ss-s); color: var(--ss-muted); margin-top:6px; }}
.ss-src {{ font-size: var(--ss-xs); color: var(--ss-muted); margin-top:10px; letter-spacing:.02em; }}
.ss-src code {{ font-family: var(--ss-mono); color: var(--ss-text2); background: transparent; padding:0; }}
.ss-card {{ background: var(--ss-s1); border:1px solid var(--ss-border); border-radius: var(--ss-radius); padding:18px 20px; animation: ss-rise .3s var(--ss-ease) both; }}
.ss-card.tight {{ padding: 14px 16px; }}
.ss-card.accent {{ border-left: 3px solid var(--ss-accent); }}
.ss-tile {{ background: var(--ss-s1); border:1px solid var(--ss-border); border-radius: var(--ss-radius); padding:14px 16px; animation: ss-rise .3s var(--ss-ease) both; min-height: 92px; }}
.ss-tile .ss-val {{ margin-top: 2px; }}
.ss-tile-row {{ display:flex; align-items:flex-end; justify-content:space-between; gap:10px; }}
.ss-delta {{ font-family: var(--ss-mono); font-size: var(--ss-s); font-weight:600; margin-top:6px; font-variant-numeric: tabular-nums; }}
@keyframes ss-rise {{ from {{ opacity:0; transform: translateY(8px); }} to {{ opacity:1; transform:none; }} }}
.ss-stagger > * {{ animation: ss-rise .3s var(--ss-ease) both; }}
{"".join(f".ss-stagger > *:nth-child({i}) {{ animation-delay: {i*40}ms; }}" for i in range(1, 11))}

/* ---------- section header ---------- */
.ss-section {{ display:flex; align-items:baseline; justify-content:space-between; gap:16px; margin: 26px 0 10px; padding-bottom:8px; border-bottom:1px solid var(--ss-border); }}
.ss-section h2 {{ font-family: var(--ss-display) !important; font-size: var(--ss-l) !important; font-weight:600 !important; letter-spacing:-.01em; margin:0 !important; padding:0 !important; color: var(--ss-text); }}
.ss-section span {{ font-size: var(--ss-s); color: var(--ss-muted); }}
.ss-page-title {{ font-family: var(--ss-display); font-size: var(--ss-l); font-weight:600; letter-spacing:-.01em; color: var(--ss-text); margin: 14px 0 2px; }}
.ss-page-sub {{ font-size: var(--ss-s); color: var(--ss-muted); margin-bottom: 16px; }}

/* ---------- instrument header ---------- */
.ss-ihead {{ display:grid; grid-template-columns: 2fr 1.1fr 1.2fr 1.3fr 1.3fr; gap: 28px; align-items:end; padding: 12px 0 20px; border-bottom:1px solid var(--ss-border); margin-bottom: 18px; }}
.ss-ihead > div {{ min-width:0; animation: ss-rise .3s var(--ss-ease) both; }}
.ss-ihead .ss-val {{ white-space:nowrap; }}
.ss-val.text {{ font-family: var(--ss-ui); font-size: var(--ss-m); font-weight:600; line-height:1.3; }}
{"".join(f".ss-ihead > div:nth-child({i}) {{ animation-delay: {i*40}ms; }}" for i in range(1, 6))}
@media (max-width: 1180px) {{ .ss-ihead {{ grid-template-columns: 1.6fr 1fr 1.2fr; }} }}
/* ---------- range bar, ring, brief, waterfall ---------- */
.ss-rbar {{ position:relative; height:4px; border-radius:2px; background: var(--ss-border2); margin:14px 0 8px; }}
.ss-rbar i {{ position:absolute; top:-4px; width:12px; height:12px; border-radius:50%; background: var(--ss-text); border:2px solid var(--ss-ink); transform:translateX(-50%); transition: left .3s var(--ss-ease); }}
.ss-rbar.accent i {{ background: var(--ss-accent); }}
.ss-rlabels {{ display:flex; justify-content:space-between; font-family: var(--ss-mono); font-size: var(--ss-s); font-weight:500; color: var(--ss-text2); }}
.ss-ring {{ position:relative; width:64px; height:64px; flex:none; }}
.ss-ring svg {{ transform: rotate(-90deg); }}
.ss-ring svg circle.v {{ transition: stroke-dashoffset .3s var(--ss-ease); }}
.ss-ring b {{ position:absolute; inset:0; display:grid; place-items:center; font-family: var(--ss-mono); font-size: var(--ss-s); font-weight:600; color: var(--ss-text); }}
.ss-brief {{ list-style:none; margin:0; padding:0; }}
.ss-brief li {{ display:flex; gap:10px; padding:8px 0; border-top:1px solid var(--ss-border); font-size: var(--ss-m); color: var(--ss-text); line-height:1.4; }}
.ss-brief li:first-child {{ border-top:0; padding-top:0; }}
.ss-brief li i {{ flex:none; width:6px; height:6px; border-radius:50%; margin-top:8px; background: var(--ss-accent); }}
.ss-callrow {{ display:flex; align-items:center; gap:22px; flex-wrap:wrap; }}
.ss-strip {{ display:flex; gap:10px; flex-wrap:wrap; margin: 6px 0 2px; }}
.ss-stage {{ display:inline-flex; align-items:center; gap:8px; padding:6px 12px; border:1px solid var(--ss-border); border-radius:999px; background: var(--ss-s1); font-size: var(--ss-s); color: var(--ss-text2); }}
.ss-stage b {{ color: var(--ss-text); font-weight:500; }}
.ss-stage .ss-dot {{ width:7px; height:7px; }}
.ss-note {{ display:flex; gap:10px; align-items:flex-start; margin: 8px 0 12px; padding:10px 14px; border:1px solid rgba(245,165,36,.35); border-radius:10px; background: rgba(245,165,36,.07); font-size: var(--ss-s); color: var(--ss-text2); line-height:1.45; }}
.ss-note.bad {{ border-color: rgba(242,85,90,.35); background: rgba(242,85,90,.07); }}
.ss-note.info {{ border-color: rgba(25,211,197,.3); background: rgba(25,211,197,.06); }}
.ss-note b {{ color: var(--ss-text); font-weight:600; }}
.ss-empty {{ padding: 26px 20px; border:1px dashed var(--ss-border2); border-radius: var(--ss-radius); text-align:center; color: var(--ss-text2); font-size: var(--ss-s); }}
.ss-empty b {{ display:block; color: var(--ss-text); font-size: var(--ss-m); font-weight:600; margin-bottom:4px; }}
.ss-empty code {{ font-family: var(--ss-mono); color: var(--ss-accent); background:transparent; }}
.ss-ncard {{ background: var(--ss-s1); border:1px solid var(--ss-border); border-radius: var(--ss-radius); padding:14px; display:flex; flex-direction:column; gap:8px; min-height: 150px; animation: ss-rise .3s var(--ss-ease) both; }}
.ss-ncard .meta {{ display:flex; justify-content:space-between; gap:8px; font-size: var(--ss-xs); color: var(--ss-muted); letter-spacing:.04em; text-transform:uppercase; }}
.ss-ncard .t {{ font-weight:600; font-size: var(--ss-s); line-height:1.35; color: var(--ss-text); flex:1; }}
.ss-ncard .t a {{ color: inherit; text-decoration:none; }} .ss-ncard .t a:hover {{ color: var(--ss-accent); }}
.ss-ncard .sm {{ font-size: var(--ss-xs); color: var(--ss-text2); line-height:1.4; }}
.ss-pbar {{ height:3px; background: var(--ss-border2); border-radius:2px; position:relative; }}
.ss-pbar i {{ position:absolute; left:50%; top:0; height:100%; background: var(--ss-up); border-radius:2px; }}
.ss-pbar i.neg {{ background: var(--ss-down); transform: translateX(-100%); }}
.ss-flow {{ display:flex; align-items:stretch; gap:8px; margin: 6px 0 4px; }}
.ss-flow .node {{ flex:1; min-width:0; background: var(--ss-s1); border:1px solid var(--ss-border); border-radius:10px; padding:10px 12px; }}
.ss-flow .node .k {{ font-size: var(--ss-xs); font-weight:600; letter-spacing:.08em; text-transform:uppercase; color: var(--ss-text2); }}
.ss-flow .node .v {{ font-family: var(--ss-display); font-weight:600; font-size: var(--ss-m); color: var(--ss-text); margin:3px 0 2px; }}
.ss-flow .node .d {{ font-size: var(--ss-xs); color: var(--ss-muted); }}
.ss-flow .arrow {{ display:flex; align-items:center; color: var(--ss-border2); font-size: 1rem; flex:none; }}
.ss-kv {{ display:grid; grid-template-columns: auto 1fr; gap: 4px 14px; font-size: var(--ss-s); }}
.ss-kv .k {{ color: var(--ss-muted); }} .ss-kv .v {{ color: var(--ss-text); font-family: var(--ss-mono); text-align:right; }}
.ss-bridge {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; font-size: var(--ss-s); color: var(--ss-text2); }}
.ss-bridge b {{ font-family: var(--ss-mono); color: var(--ss-text); font-weight:600; font-size: var(--ss-m); }}
.ss-bridge .arr {{ color: var(--ss-border2); }}
.ss-banner {{ border-radius:10px; padding:10px 14px; font-size: var(--ss-s); font-weight:500; margin-top:12px; border:1px solid; }}
.ss-banner.buy {{ background: rgba(34,197,94,.10); border-color: rgba(34,197,94,.35); color: var(--ss-up); }}
.ss-banner.sell {{ background: rgba(242,85,90,.10); border-color: rgba(242,85,90,.35); color: var(--ss-down); }}
.ss-banner.hold {{ background: rgba(96,165,250,.10); border-color: rgba(96,165,250,.35); color: var(--ss-blue); }}
.ss-banner.cash {{ background: var(--ss-s2); border-color: var(--ss-border2); color: var(--ss-text2); }}
.ss-footer {{ margin-top:40px; padding-top:14px; border-top:1px solid var(--ss-border); font-size: var(--ss-xs); color: var(--ss-muted); letter-spacing:.06em; text-transform:uppercase; display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; }}
.st-key-btn_play kbd, .st-key-btn_next kbd, .st-key-btn_reset kbd {{ display:none; }}
.ss-kbd {{ display:inline-block; font-family: var(--ss-mono); font-size: var(--ss-xs); padding:1px 6px; border:1px solid var(--ss-border2); border-bottom-width:2px; border-radius:4px; color: var(--ss-text2); background: var(--ss-s2); }}

/* ---------- native widget polish ---------- */
div[data-testid="stVerticalBlockBorderWrapper"] {{ background: var(--ss-s1); border: 1px solid var(--ss-border) !important; border-radius: var(--ss-radius); animation: ss-rise .3s var(--ss-ease) both; }}
div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] {{ gap: 0.6rem; }}
[data-testid="stPageLink"] a {{ border:1px solid var(--ss-border); border-radius: 10px; padding: 8px 12px; background: var(--ss-s1); font-weight:600; font-size: var(--ss-s); color: var(--ss-text) !important; width:100%; transition: border-color .2s var(--ss-ease); }}
[data-testid="stPageLink"] a:hover {{ border-color: var(--ss-accent); text-decoration:none; }}
div[data-testid="stMetric"] {{ background: var(--ss-s1); border:1px solid var(--ss-border); border-radius: var(--ss-radius); padding: 12px 16px; animation: ss-rise .3s var(--ss-ease) both; }}
div[data-testid="stMetricLabel"] p {{ font-size: var(--ss-xs) !important; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color: var(--ss-text2); }}
div[data-testid="stMetricValue"] {{ font-size: var(--ss-l) !important; font-weight:600; color: var(--ss-text); }}
div[data-testid="stMetricDelta"] {{ font-family: var(--ss-mono); font-size: var(--ss-s); }}
.stButton > button, .stDownloadButton > button, [data-testid="stPopover"] > button {{ border-radius:8px; border:1px solid var(--ss-border2); font-family: var(--ss-ui); font-weight:600; font-size: var(--ss-s); transition: border-color .2s var(--ss-ease), background .2s var(--ss-ease); }}
.stButton > button[kind="primary"] {{ background: var(--ss-accent); color: var(--ss-accent-ink); border-color: var(--ss-accent); }}
.stButton > button[kind="primary"]:hover {{ background: #3EE0D3; border-color: #3EE0D3; color: var(--ss-accent-ink); }}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{ outline: 2px solid var(--ss-accent); outline-offset: 2px; }}
[data-testid="stExpander"] details {{ border:1px solid var(--ss-border); border-radius: var(--ss-radius); background: var(--ss-s1); }}
[data-testid="stExpander"] summary {{ font-weight:600; font-size: var(--ss-s); }}
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid var(--ss-border); }}
.stTabs [data-baseweb="tab"] {{ font-size: var(--ss-s); font-weight:600; color: var(--ss-text2); padding: 8px 12px; }}
.stTabs [aria-selected="true"] {{ color: var(--ss-text); }}
.stTabs [data-baseweb="tab-highlight"] {{ background: var(--ss-accent); }}
[data-testid="stDataFrame"] {{ border:1px solid var(--ss-border); border-radius: 10px; overflow:hidden; }}
[data-testid="stCaptionContainer"] p {{ color: var(--ss-muted); font-size: var(--ss-s); }}
[data-testid="stPills"] button, [data-testid="stSegmentedControl"] button {{ font-size: var(--ss-s); font-weight:500; }}
[data-testid="stAlert"] {{ border-radius: 10px; font-size: var(--ss-s); }}
.stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] {{ font-family: var(--ss-mono); font-size: var(--ss-xs); }}
[data-testid="stToast"] {{ font-family: var(--ss-ui); border:1px solid var(--ss-border2); background: var(--ss-s2); color: var(--ss-text); border-radius:10px; }}
.st-key-ss_runtime {{ position:absolute; height:0 !important; width:0; overflow:hidden; margin:0 !important; min-height:0; opacity:0; pointer-events:none; }}
[data-testid="stTooltipIcon"] {{ color: var(--ss-muted); }}
label[data-testid="stWidgetLabel"] p {{ font-size: var(--ss-xs); font-weight:600; letter-spacing:.06em; text-transform:uppercase; color: var(--ss-text2); }}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition: none !important; }}
}}
@media (max-width: 1400px) {{
  .ss-hero {{ font-size: 2.3rem; }}
}}
@media (max-width: 1100px) {{
  .ss-hero {{ font-size: 2rem; }}
  .ss-appbar .ss-asof {{ display:none; }}
}}
</style>
"""


CUSTOM_CSS = build_css()
