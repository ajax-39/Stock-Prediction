# Feature-parity checklist (HEAD `7b0a89cd` → Stock sight)

Legend: `[ ]` pending · `[x]` present and working · `[~]` kept but changed (reason given) · `[!]` dropped (reason given)

## Global (app.py sidebar at HEAD)
- [ ] Market open/closed status with IST clock
- [ ] Instrument selector (single option RELIANCE.NS)
- [ ] Cluster telemetry (HDFS/Hive/HBase/Kafka) — hardcoded "ONLINE" at HEAD; must become file-based freshness
- [ ] "Run Batch Prediction Pipeline" button → run_pig_etl → spark_feature_engineering → spark_score_engine → predict_next_day, spinner, success, error, rerun
- [ ] Stack caption (Hadoop · Spark · Hive · HBase · Kafka)

## Home (app.py)
- [ ] Current price (last close) with change
- [ ] Next-day forecast with predicted return %
- [ ] Composite score
- [ ] Signal
- [ ] Model confidence
- [ ] Navigation to the four pages (cards → st.page_link)
- [ ] End-to-end pipeline flow overview

## Page 1 · Pipeline & Data
- [ ] 5-stage architecture flow (Sources → HDFS → Pig/MR → Spark/ML → HBase/Hive)
- [ ] Kaggle OHLCV metrics: sessions, timeline range, highest close, average volume
- [ ] Raw price table expander with rows slider (5–50)
- [ ] News cards: source, sentiment chip with polarity, title, summary, date
- [ ] Macro metrics: sector, sector P/E, NIFTY sentiment score + label, Brent crude
- [ ] HDFS 3-zone hierarchy table (tab)
- [ ] Hive warehouse schema SQL (tab)
- [ ] Missing-data warnings for each source

## Page 2 · Technicals
- [ ] Time range selector (60D / 180D / 1Y / All)
- [ ] Overlay toggles: EMA 20, EMA 50, VWAP, Bollinger Bands
- [ ] Candlestick chart with overlays
- [ ] Volume panel (up/down coloured)
- [ ] RSI panel with 70/30 lines
- [ ] MACD panel: MACD, signal, histogram
- [ ] Indicator summary table (RSI, MACD, EMA 20 vs 50, BB position) with interpretation
- [ ] Multi-factor scores T, F, N, R, S with dominant factor
- [ ] Composite formula caption
- [ ] Momentum: 30d, 60d, 90d returns, volume trend

## Page 3 · Prediction
- [ ] Target date
- [ ] Predicted close, ₹ delta and % delta, direction glyph
- [ ] Current close
- [ ] Confidence interval (lower–upper)
- [ ] Signal badge
- [ ] Model confidence %
- [ ] HBase rowkey of the latest serving record
- [ ] Feature importance bar chart
- [ ] Model MAE (+ improvement vs naive), RMSE, directional hit rate, naive MAE
- [ ] Walk-forward "actual vs predicted" curve — at HEAD the predicted curve is `actual + sin()` noise (fabricated). Replace with a computed view and say so.
- [ ] Baseline comparison table (MAE, RMSE, directional) — HEAD hardcodes "50.0%" and "+14.2% alpha"; must be computed
- [ ] Link to the backtest page

## Page 4 · Backtest
- [ ] Horizon selectbox (1 / 2 / 3 months) resets the replay
- [ ] Cumulative net P&L (₹ and %)
- [ ] Session P&L (₹ and %, ▲/▼/▬)
- [ ] Portfolio equity with cash and shares
- [ ] Trade win rate with wins / losses
- [ ] Timeline: day n / N, date, % progress
- [ ] Play / Pause button
- [ ] Next day button (disabled while playing)
- [ ] Reset button
- [ ] Speed choice 1s / 3s / 5s / 10s
- [ ] Timeline step slider
- [ ] Price bridge: yesterday → today (Δ) → tomorrow forecast
- [ ] Predicted close with Δ ₹ and % and direction glyph
- [ ] Forecast cone (lower–upper) and target date
- [ ] Action banner: BUY executed / HOLDING / SELL executed / CASH
- [ ] Signal badge, confidence, position size
- [ ] Driver metrics: composite, RSI, technical, VWAP spread (with state text)
- [ ] Candlestick chart revealed to current step, fixed x-range
- [ ] EMA 20 overlay
- [ ] BUY / SELL markers with P&L text, LONG marker when in position
- [ ] Forecast projection line and CI band
- [ ] Volume panel
- [ ] Equity curve vs passive buy & hold, ₹1,00,000 baseline line, anchored y-range
- [ ] Alpha vs buy & hold note
- [ ] Active open-position card / "no position" state
- [ ] Closed-trade ledger (#, entry, exit, buy, sell, P&L, return, status)
- [ ] Day-by-day audit log expander (11 columns)
- [ ] Automatic playback loop at chosen speed
- [ ] End-of-horizon completion message

## data_loader.py public API (must keep names and return shapes)
- [ ] load_raw_prices, load_curated_news, load_market_sentiment, load_engineered_features, load_daily_scores, load_sector_momentum, load_predictions, load_model_metrics, load_latest_serving_state

## Launchers
- [ ] `python run.py`, `--pipeline-only`, `--dashboard-only`
