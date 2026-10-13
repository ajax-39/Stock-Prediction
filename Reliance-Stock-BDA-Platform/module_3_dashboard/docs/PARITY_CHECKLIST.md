# Feature-parity checklist (HEAD `7b0a89cd` → Stock sight)

Completed 13 Oct 2026. Every item was exercised in the browser at 1440 px and 1024 px.

Legend: `[ ]` pending · `[x]` present and working · `[~]` kept but changed (reason given) · `[!]` dropped (reason given)

## Global (app.py sidebar at HEAD)
- [x] Market open/closed status with IST clock
- [x] Instrument selector (single option RELIANCE.NS) — kept in the sidebar
- [~] Cluster telemetry (HDFS/Hive/HBase/Kafka) — the hardcoded "ONLINE" badges are replaced by the pipeline-health strip (home) and the stage-status table (Pipeline & Data), both read from the files on disk. Nothing in the app can see the Docker cluster, so claiming it is online would be a made-up label.
- [x] "Run Batch Prediction Pipeline" button → run_pig_etl → spark_feature_engineering → spark_score_engine → predict_next_day, spinner, success, error, rerun
- [x] Stack caption (Hadoop · Spark · Hive · HBase · Kafka)

## Home (app.py)
- [x] Current price (last close) with change
- [x] Next-day forecast with predicted return %
- [x] Composite score
- [x] Signal
- [x] Model confidence
- [~] Navigation to the four pages — the four marketing cards became a row of `st.page_link` buttons; their copy ("realistic 68.2% accuracy", "positive net green PnL") was hardcoded and is gone
- [~] End-to-end pipeline flow overview — the ASCII block is replaced by the pipeline-health strip on the home page and the flow diagram on Pipeline & Data

## Page 1 · Pipeline & Data
- [x] 5-stage architecture flow (Sources → HDFS → Pig/MR → Spark/ML → HBase/Hive)
- [x] Kaggle OHLCV metrics: sessions, timeline range, highest close, average volume
- [x] Raw price table expander with rows slider (5–50)
- [x] News cards: source, sentiment chip with polarity, title, summary, date
- [x] Macro metrics: sector, sector P/E, NIFTY sentiment score + label, Brent crude (+ India VIX and FII/DII flow, which are in the file; the hardcoded deltas "Historical Mean" / "Stable Input Cost" are gone)
- [~] HDFS 3-zone hierarchy table (tab) — the "✅ MOUNTED" column now reports whether the local mirror of each path is staged, from disk
- [x] Hive warehouse schema SQL (tab)
- [x] Missing-data warnings for each source

## Page 2 · Technicals
- [x] Time range selector (60D / 180D / 1Y / All) — segmented control, plus a Custom from–to date range
- [x] Overlay toggles: EMA 20, EMA 50, VWAP, Bollinger Bands — multi-select pills
- [x] Candlestick chart with overlays
- [x] Volume panel (up/down coloured)
- [x] RSI panel with 70/30 lines
- [x] MACD panel: MACD, signal, histogram
- [x] Indicator summary table (RSI, MACD, EMA 20 vs 50, BB position) with interpretation — plus close vs VWAP, volume ratio, and each rule's sub-score → effect on T
- [x] Multi-factor scores T, F, N, R, S with dominant factor
- [x] Composite formula caption
- [x] Momentum: 30d, 60d, 90d returns, volume trend

## Page 3 · Prediction
- [x] Target date
- [x] Predicted close, ₹ delta and % delta, direction glyph
- [x] Current close
- [x] Confidence interval (lower–upper)
- [x] Signal badge
- [x] Model confidence %
- [x] HBase rowkey of the latest serving record
- [x] Feature importance bar chart
- [x] Model MAE (+ improvement vs naive), RMSE, directional hit rate, naive MAE
- [!] Walk-forward "actual vs predicted" curve — at HEAD the predicted curve was `actual + sin()` noise (fabricated). Replaced by the actual close vs the naive baseline over the real test window, with a caption saying why; the pipeline does not persist per-day model predictions
- [x] Baseline comparison table (MAE, RMSE, directional) — edges computed from the metrics file; a sign-persistence baseline is computed from the features; the hardcoded "+14.2% alpha" is gone
- [x] Link to the backtest page — via the sidebar nav and the home page links (the gradient CTA banner is gone)

## Page 4 · Backtest
- [x] Horizon selectbox (1 / 2 / 3 months) resets the replay
- [x] Cumulative net P&L (₹ and %)
- [x] Session P&L (₹ and %, ▲/▼/▬)
- [x] Portfolio equity with cash and shares
- [x] Trade win rate with wins / losses
- [x] Timeline: day n / N, date, % progress
- [x] Play / Pause button
- [x] Next day button (disabled while playing)
- [x] Reset button
- [x] Speed choice 1s / 3s / 5s / 10s — segmented control
- [x] Timeline step slider
- [x] Price bridge: yesterday → today (Δ) → tomorrow forecast
- [x] Predicted close with Δ ₹ and % and direction glyph
- [x] Forecast cone (lower–upper) and target date
- [x] Action banner: BUY executed / HOLDING / SELL executed / CASH
- [x] Signal badge, confidence, position size
- [x] Driver metrics: composite, RSI, technical, VWAP spread (with state text)
- [x] Candlestick chart revealed to current step, fixed x-range
- [x] EMA 20 overlay
- [x] BUY / SELL markers with P&L text, LONG marker when in position
- [x] Forecast projection line and CI band
- [x] Volume panel
- [x] Equity curve vs passive buy & hold, ₹1,00,000 baseline line, anchored y-range
- [x] Alpha vs buy & hold note — factual: strategy %, buy & hold %, alpha, max drawdown
- [x] Active open-position card / "no position" state
- [x] Closed-trade ledger (#, entry, exit, buy, sell, P&L, return, status)
- [x] Day-by-day audit log expander (11 columns)
- [x] Automatic playback loop at chosen speed — a timer fragment advances one bar per tick instead of a blocking `time.sleep`, so Pause responds immediately
- [x] End-of-horizon completion message — now states the computed P&L instead of "positive net green PnL"

## data_loader.py public API (must keep names and return shapes)
- [x] load_raw_prices, load_curated_news, load_market_sentiment, load_engineered_features, load_daily_scores, load_sector_momentum, load_predictions, load_model_metrics, load_latest_serving_state

## Launchers
- [x] `python run.py`, `--pipeline-only`, `--dashboard-only` — untouched; `--dashboard-only` verified to reach Streamlit start (port 8501 was occupied by another process on the dev machine, so the app itself was verified on 8502 with the same command line)

## Added (not at HEAD)
- [x] Stock sight app bar on every page (mark, wordmark, instrument, market status with live dot, as-of date, signal badge)
- [x] Ticker tape (last close, RSI, composite, signal, forecast, latest headline with sentiment chip), pauses on hover
- [x] `theme.py` tokens + shared Plotly template; `components.py` helpers; single `set_page_config` / CSS injection via `st.navigation`
- [x] `.streamlit/config.toml` mirroring the tokens; SVG favicon and `st.logo`
- [x] Home: instrument header (day range, 52-week range bar, volume vs 20-day with sparkline), tomorrow's call with fan chart and confidence ring, rule-based brief, composite gauge, contribution waterfall, pipeline-health strip, news feed with overlap warning, HBase-vs-CSV mismatch warning
- [x] Pipeline & Data: stage-status table, data-quality panel (missing values, duplicate dates, date gaps, news→price join rate), synthetic-vs-Kaggle detection, staged previews tab
- [x] Technicals: custom date range, indicator → state → sub-score table, score history chart, daily-returns calendar heatmap
- [x] Prediction: "why this signal" rules, honest model card with verdict, sign-persistence baseline, serving log
- [x] Backtest: media-player bar, keyboard shortcuts (Space / → / Home; Streamlit reserves R), max drawdown, trade toasts, WIN/LOSS row tinting, CSV downloads
- [x] Sidebar: instrument, as-of date, price source detected from data, model, signal, pipeline button (same four scripts, same order), glossary popover
- [x] CSV download on every table; date-range filters on time-series views; explicit empty/missing-file states
