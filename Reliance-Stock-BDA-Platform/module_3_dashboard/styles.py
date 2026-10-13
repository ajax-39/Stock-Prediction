"""
styles.py — Professional Financial Design System for Reliance Stock Analytics
==============================================================================
Implements a restrained, high-density financial terminal aesthetic inspired by
professional market analytics platforms.
"""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ===== CORE TYPOGRAPHY & LAYOUT ===== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-feature-settings: 'tnum' 1;  /* Tabular numerals for financial values */
    }

    .stApp {
        background: #0B0E14;
        color: #E6EAF0;
    }

    /* ===== SIDEBAR ===== */
    section[data-testid="stSidebar"] {
        background: #121722;
        border-right: 1px solid #273142;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
    }

    /* ===== HEADINGS ===== */
    h1 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #E6EAF0 !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.02em !important;
    }

    h2 {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: #E6EAF0 !important;
        margin: 1.5rem 0 0.75rem 0 !important;
        letter-spacing: -0.01em !important;
    }

    h3 {
        font-size: 0.9375rem !important;
        font-weight: 600 !important;
        color: #E6EAF0 !important;
        margin: 1rem 0 0.5rem 0 !important;
    }

    /* ===== PANELS & CARDS ===== */
    .financial-panel {
        background: #121722;
        border: 1px solid #273142;
        border-radius: 6px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .financial-panel-secondary {
        background: #181F2B;
        border: 1px solid #273142;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }

    /* ===== INSTRUMENT HEADER ===== */
    .instrument-header {
        background: #121722;
        border: 1px solid #273142;
        border-radius: 6px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }

    .instrument-name {
        font-size: 1.125rem;
        font-weight: 600;
        color: #E6EAF0;
        margin-bottom: 0.25rem;
    }

    .instrument-symbol {
        font-size: 0.8125rem;
        color: #929BAD;
        margin-bottom: 0.5rem;
    }

    .instrument-price {
        font-size: 2.25rem;
        font-weight: 700;
        color: #E6EAF0;
        line-height: 1;
        margin: 0.5rem 0;
    }

    .price-change-positive {
        color: #22C55E;
        font-size: 1rem;
        font-weight: 600;
    }

    .price-change-negative {
        color: #EF4444;
        font-size: 1rem;
        font-weight: 600;
    }

    .price-change-neutral {
        color: #929BAD;
        font-size: 1rem;
        font-weight: 600;
    }

    /* ===== STATUS INDICATORS ===== */
    .status-live {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        background: rgba(34, 197, 94, 0.1);
        color: #22C55E;
        border: 1px solid rgba(34, 197, 94, 0.2);
        padding: 0.25rem 0.625rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    .status-closed {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        background: rgba(146, 155, 173, 0.1);
        color: #929BAD;
        border: 1px solid rgba(146, 155, 173, 0.2);
        padding: 0.25rem 0.625rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    .status-delayed {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        background: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.2);
        padding: 0.25rem 0.625rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    /* ===== TRADING SIGNALS ===== */
    .signal-buy {
        background: rgba(34, 197, 94, 0.15);
        color: #22C55E;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }

    .signal-hold {
        background: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }

    .signal-sell {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.875rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
    }

    /* ===== METRIC GROUPS ===== */
    .metric-label {
        font-size: 0.75rem;
        color: #929BAD;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }

    .metric-value {
        font-size: 1.25rem;
        color: #E6EAF0;
        font-weight: 600;
        line-height: 1.2;
    }

    .metric-value-large {
        font-size: 1.875rem;
        color: #E6EAF0;
        font-weight: 700;
        line-height: 1;
    }

    .metric-secondary {
        font-size: 0.8125rem;
        color: #929BAD;
        margin-top: 0.25rem;
    }

    /* ===== FORECAST CARD ===== */
    .forecast-card {
        background: #181F2B;
        border: 1px solid #273142;
        border-left: 3px solid #60A5FA;
        border-radius: 6px;
        padding: 1.25rem;
        margin: 1.5rem 0;
    }

    .forecast-label {
        font-size: 0.6875rem;
        color: #929BAD;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .forecast-price {
        font-size: 2rem;
        font-weight: 700;
        color: #E6EAF0;
        line-height: 1;
    }

    .forecast-comparison {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1rem 0;
        font-size: 0.9375rem;
        color: #929BAD;
    }

    .forecast-arrow {
        font-size: 1.5rem;
        color: #60A5FA;
    }

    /* ===== DATA TABLES ===== */
    .dataframe {
        font-size: 0.8125rem !important;
    }

    .dataframe th {
        background: #181F2B !important;
        color: #929BAD !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.6875rem !important;
        letter-spacing: 0.025em !important;
        padding: 0.5rem !important;
        border-bottom: 1px solid #273142 !important;
    }

    .dataframe td {
        background: #121722 !important;
        color: #E6EAF0 !important;
        padding: 0.5rem !important;
        border-bottom: 1px solid #273142 !important;
    }

    /* ===== STREAMLIT METRIC OVERRIDES ===== */
    div[data-testid="stMetric"] {
        background: #181F2B;
        border: 1px solid #273142;
        border-radius: 6px;
        padding: 1rem;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        color: #929BAD;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #E6EAF0;
    }

    div[data-testid="stMetricDelta"] svg {
        display: none;
    }

    /* ===== SENTIMENT CHIPS ===== */
    .sentiment-positive {
        background: rgba(34, 197, 94, 0.15);
        color: #22C55E;
        border: 1px solid rgba(34, 197, 94, 0.25);
        padding: 0.125rem 0.5rem;
        border-radius: 3px;
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        display: inline-block;
    }

    .sentiment-negative {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.25);
        padding: 0.125rem 0.5rem;
        border-radius: 3px;
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        display: inline-block;
    }

    .sentiment-neutral {
        background: rgba(146, 155, 173, 0.15);
        color: #929BAD;
        border: 1px solid rgba(146, 155, 173, 0.25);
        padding: 0.125rem 0.5rem;
        border-radius: 3px;
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        display: inline-block;
    }

    /* ===== DIVIDERS ===== */
    hr {
        border: none;
        border-top: 1px solid #273142;
        margin: 1.5rem 0;
    }

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: #E6EAF0 !important;
        background: #181F2B !important;
        border: 1px solid #273142 !important;
        border-radius: 6px !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #121722;
        padding: 0.5rem;
        border-radius: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: 1px solid transparent;
        color: #929BAD;
        font-size: 0.8125rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 4px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #181F2B;
        color: #E6EAF0;
    }

    .stTabs [aria-selected="true"] {
        background: #181F2B;
        border-color: #60A5FA;
        color: #E6EAF0;
    }

    /* ===== UTILITY CLASSES ===== */
    .text-muted {
        color: #929BAD;
        font-size: 0.8125rem;
    }

    .text-small {
        font-size: 0.75rem;
        color: #929BAD;
    }

    .text-warning {
        color: #F59E0B;
    }

    .text-success {
        color: #22C55E;
    }

    .text-error {
        color: #EF4444;
    }

    .code-inline {
        background: #181F2B;
        border: 1px solid #273142;
        border-radius: 3px;
        padding: 0.125rem 0.375rem;
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        font-size: 0.8125rem;
        color: #60A5FA;
    }
</style>
"""
