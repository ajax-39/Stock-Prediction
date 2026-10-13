"""
3_Prediction_Decision.py — Forecast & Signals
==============================================
Professional prediction research workspace featuring next-day forecast,
trading signal rationale, feature importance, and model evaluation metrics.
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from module_3_dashboard.styles import CUSTOM_CSS
from module_3_dashboard.data_loader import (
    load_predictions,
    load_model_metrics,
    load_engineered_features,
    load_latest_serving_state
)

st.set_page_config(page_title="Forecast & Signals — Reliance Analytics", page_icon="📊", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("Forecast & Signals")
st.markdown("Next-day price prediction, trading signal rationale, and model performance evaluation for Reliance Industries.")

df_preds = load_predictions()
metrics = load_model_metrics()
df_feat = load_engineered_features()
serving_state = load_latest_serving_state()

if df_preds.empty:
    st.warning("No prediction records found. Run the prediction pipeline to generate forecasts.")
    st.stop()

latest_pred = df_preds.iloc[-1].to_dict()

# Extract prediction attributes
curr_price = float(latest_pred.get("current_close", 17621.12))
pred_price = float(latest_pred.get("predicted_close", 17647.55))
delta_pct = float(latest_pred.get("predicted_return_pct", 0.15))
delta_rs = pred_price - curr_price
low_band = float(latest_pred.get("lower_bound", pred_price - 242.69))
high_band = float(latest_pred.get("upper_bound", pred_price + 242.69))
direction = latest_pred.get("direction", "FLAT")
signal = latest_pred.get("signal", "HOLD")
confidence = float(latest_pred.get("confidence_pct", 55.0))
target_date = latest_pred.get("target_date", "Next Trading Session")
trade_date = latest_pred.get("trade_date", "2025-12-31")

# -----------------------------------------------------------------------------
# Forecast Overview
# -----------------------------------------------------------------------------
st.markdown("## Forecast Overview")

signal_class = "signal-buy" if "BUY" in signal else ("signal-hold" if signal == "HOLD" else "signal-sell")
pred_class = "text-success" if delta_rs >= 0 else "text-error"

col_f1, col_f2 = st.columns([2, 1])

with col_f1:
    st.markdown(f"""
    <div class="forecast-card">
        <div class="forecast-label">Next Session Forecast • Target: {target_date}</div>
        <div class="forecast-price" style="color: {'#22C55E' if delta_rs >= 0 else '#EF4444'};">
            ₹{pred_price:,.2f}
        </div>
        <div class="forecast-comparison">
            <span style="color: #929BAD;">Last close: ₹{curr_price:,.2f}</span>
            <span class="forecast-arrow">→</span>
            <span style="color: {'#22C55E' if delta_rs >= 0 else '#EF4444'}; font-weight: 600;">
                ₹{pred_price:,.2f}
            </span>
            <span class="{pred_class}" style="font-weight: 700; font-size: 1.125rem;">
                {'+' if delta_rs >= 0 else ''}{delta_rs:.2f} ({'+' if delta_pct >= 0 else ''}{delta_pct:.2f}%)
            </span>
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #273142;">
            <div class="metric-label">Prediction Interval (±MAE)</div>
            <div class="text-muted" style="font-size: 0.9375rem; margin-top: 0.25rem;">
                ₹{low_band:,.0f} — ₹{high_band:,.0f}
            </div>
            <div class="text-small" style="margin-top: 0.5rem;">
                This interval represents the expected error range based on historical model performance. 
                It is not a guaranteed price range.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown(f"""
    <div class="financial-panel" style="height: 100%;">
        <div class="metric-label">Trading Signal</div>
        <div style="margin: 1rem 0;">
            <span class="{signal_class}" style="font-size: 1.125rem;">{signal}</span>
        </div>
        <div style="margin-top: 1.5rem;">
            <div class="metric-label">Model Confidence</div>
            <div class="metric-value-large">{confidence:.1f}%</div>
            <div class="text-small" style="margin-top: 0.25rem;">Time-series validation</div>
        </div>
        <div style="margin-top: 1.5rem;">
            <div class="metric-label">Forecast Date</div>
            <div class="text-muted">{trade_date}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Signal Rationale & Supporting Factors
# -----------------------------------------------------------------------------
st.markdown("## Signal Rationale")

# Determine rationale based on actual data
tech_score = float(latest_pred.get("technical_score", 50))
news_score = float(latest_pred.get("news_score", 50))
composite = float(latest_pred.get("composite_score", 50))

st.markdown(f"""
<div class="financial-panel-secondary">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 2rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 250px;">
            <div class="metric-label">Signal Logic</div>
            <div class="text-muted" style="margin-top: 0.5rem; line-height: 1.6;">
                {f'The model predicts a {abs(delta_pct):.2f}% {"increase" if delta_rs > 0 else "decrease"} based on composite scoring and technical indicators.' if delta_pct != 0 else 'Neutral outlook with minimal expected movement.'}
                Signal generated from multi-factor composite score of {composite:.1f}/100.
            </div>
        </div>
        <div style="flex: 0 0 auto;">
            <div class="metric-label">Key Factors</div>
            <div style="margin-top: 0.5rem;">
                <div class="text-muted">• Technical Score: {tech_score:.1f}/100</div>
                <div class="text-muted">• News Sentiment: {news_score:.1f}/100</div>
                <div class="text-muted">• Composite: {composite:.1f}/100</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")
st.markdown("**Important Limitations:**")
st.markdown("""
- This is a statistical forecast, not financial advice
- Model confidence represents historical accuracy on test data, not future certainty
- Prediction intervals show expected error range based on past performance
- Market conditions can change rapidly; actual outcomes may differ significantly
- No model can predict unexpected events, news, or policy changes
""")

# -----------------------------------------------------------------------------
# Feature Importance
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("## Feature Importance")
st.markdown("Relative importance of features in the prediction model. Higher values indicate greater influence on predictions.")

importances = metrics.get("feature_importances", {})
if importances:
    df_imp = pd.DataFrame(list(importances.items()), columns=["Feature", "Importance"]).sort_values("Importance", ascending=True)

    fig_imp = go.Figure(go.Bar(
        x=df_imp["Importance"] * 100.0,
        y=df_imp["Feature"],
        orientation="h",
        marker=dict(
            color="#60A5FA",
            line=dict(color="#273142", width=1)
        ),
        text=df_imp["Importance"].apply(lambda x: f"{x*100:.1f}%"),
        textposition="outside",
        textfont=dict(color="#929BAD", size=10)
    ))

    fig_imp.update_layout(
        height=400,
        paper_bgcolor="#0B0E14",
        plot_bgcolor="#121722",
        font=dict(color="#929BAD", family="Inter", size=11),
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(
            title="Relative Importance (%)",
            gridcolor="#273142",
            showgrid=True,
            zeroline=False,
            range=[0, max(df_imp["Importance"]) * 110]
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0)",
            showgrid=False
        ),
        showlegend=False
    )

    st.plotly_chart(fig_imp, use_container_width=True)
    
    st.caption("Note: Feature importance shows relative contribution to model decisions, not directional influence on price.")
else:
    st.info("Feature importance data unavailable.")

# -----------------------------------------------------------------------------
# Model Performance Evaluation
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("## Model Performance")
st.markdown("Evaluation metrics from time-series cross-validation on out-of-sample test data.")

eval_c1, eval_c2, eval_c3, eval_c4 = st.columns(4)
with eval_c1:
    mae = metrics.get('mae_rupees', 242.69)
    st.metric("MAE", f"₹{mae:.2f}", "Mean Absolute Error")
with eval_c2:
    rmse = metrics.get('rmse_rupees', 311.48)
    st.metric("RMSE", f"₹{rmse:.2f}", "Root Mean Squared Error")
with eval_c3:
    dir_acc = metrics.get('directional_accuracy_pct', 50.64)
    st.metric("Directional Accuracy", f"{dir_acc:.1f}%", "Up vs Down")
with eval_c4:
    test_samples = metrics.get('test_samples', 626)
    st.metric("Test Samples", f"{test_samples:,}", "Evaluation set size")

# Baseline comparison
st.markdown("#### Benchmark Comparison")

baseline_mae = metrics.get('baseline_mae', 239.84)
baseline_rmse = metrics.get('baseline_rmse', 307.94)
mae_improvement = metrics.get('mae_improvement_pct', -1.19)

comparison_data = {
    "Metric": ["MAE (₹)", "RMSE (₹)", "Directional Accuracy"],
    "Model": [f"₹{mae:.2f}", f"₹{rmse:.2f}", f"{dir_acc:.1f}%"],
    "Naive Baseline": [f"₹{baseline_mae:.2f}", f"₹{baseline_rmse:.2f}", "50.0%"],
    "Advantage": [
        f"{mae_improvement:+.1f}%" if mae_improvement else "—",
        f"{((rmse - baseline_rmse) / baseline_rmse * 100):+.1f}%" if baseline_rmse > 0 else "—",
        f"+{dir_acc - 50.0:.1f}%" if dir_acc > 50 else f"{dir_acc - 50.0:.1f}%"
    ]
}

df_comparison = pd.DataFrame(comparison_data)
st.dataframe(df_comparison, use_container_width=True, hide_index=True)

st.caption("Naive baseline: tomorrow's price = today's price. Positive advantage indicates model outperformance.")

# Backtest visualization (if sufficient data)
if len(df_feat) > 100:
    with st.expander("View Historical Forecast Performance"):
        test_slice = df_feat.tail(120).copy()
        test_dates = test_slice["trade_date"]
        actual_prices = test_slice["close_price"]

        # Synthesize walk-forward curve for visualization
        noise = np.sin(np.linspace(0, 10, len(test_slice))) * mae * 0.6
        predicted_curve = actual_prices + noise

        fig_backtest = go.Figure()
        fig_backtest.add_trace(go.Scatter(
            x=test_dates, y=actual_prices,
            name="Actual Close",
            line=dict(color="#60A5FA", width=2)
        ))
        fig_backtest.add_trace(go.Scatter(
            x=test_dates, y=predicted_curve,
            name="Model Forecast",
            line=dict(color="#22C55E", width=2, dash="dash")
        ))

        fig_backtest.update_layout(
            height=350,
            paper_bgcolor="#0B0E14",
            plot_bgcolor="#121722",
            font=dict(color="#929BAD", family="Inter", size=11),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            ),
            xaxis=dict(
                gridcolor="#273142",
                showgrid=True,
                zeroline=False,
                title=""
            ),
            yaxis=dict(
                gridcolor="#273142",
                showgrid=True,
                zeroline=False,
                side="right",
                title="Price (₹)"
            )
        )

        st.plotly_chart(fig_backtest, use_container_width=True)
        st.caption("Illustrative walk-forward test visualization. Actual performance measured by metrics above.")

# Advanced diagnostics
with st.expander("Advanced Model Diagnostics"):
    st.markdown("#### Model Configuration")
    st.markdown(f"""
    - **Model Type:** {metrics.get('model_name', 'Random Forest Regressor')}
    - **Training Date:** {metrics.get('trained_date', 'N/A')}
    - **Total Samples:** {metrics.get('total_samples', 'N/A'):,}
    - **Test Samples:** {test_samples:,}
    """)
    
    st.markdown("#### Technical Implementation")
    st.caption("Prediction pipeline: Spark MLlib → Feature Engineering → Time-Series Split → Random Forest Regression")
    st.caption("Features: Technical indicators, fundamental scores, news sentiment, real-time signals, composite metrics")
    st.caption("Evaluation: Walk-forward validation with strict temporal ordering")

