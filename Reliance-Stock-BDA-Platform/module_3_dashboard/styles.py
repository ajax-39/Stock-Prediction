"""
styles.py — Design System & Custom Glassmorphic Styles for Reliance Dashboard
=============================================================================
"""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main background */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #111827 0%, #0a0e17 100%);
        color: #f3f4f6;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b0f19 0%, #111827 50%, #0a0e17 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(17, 24, 39, 0.65);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(16, 185, 129, 0.3);
        transform: translateY(-2px);
    }

    /* Hero Prediction Card */
    .hero-pred-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(17, 24, 39, 0.85) 100%);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 40px rgba(16, 185, 129, 0.15);
    }

    /* Status Badges */
    .badge-online {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    .badge-signal-buy {
        background: linear-gradient(135deg, #059669, #10b981);
        color: white;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: 0 0 18px rgba(16, 185, 129, 0.45);
        display: inline-block;
    }

    .badge-signal-hold {
        background: linear-gradient(135deg, #d97706, #f59e0b);
        color: white;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: 0 0 18px rgba(245, 158, 11, 0.4);
        display: inline-block;
    }

    .badge-signal-sell {
        background: linear-gradient(135deg, #dc2626, #ef4444);
        color: white;
        padding: 6px 18px;
        border-radius: 30px;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: 0 0 18px rgba(239, 68, 68, 0.45);
        display: inline-block;
    }

    .sentiment-chip-pos {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .sentiment-chip-neg {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Metric cards override */
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 18px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f9fafb;
    }
</style>
"""
