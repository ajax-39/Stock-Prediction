-- ============================================================================
-- hive_queries.sql — Analytical HiveQL Queries & Materialized Views
-- ============================================================================

USE reliance_bda_db;

-- 1. View: Daily Summary with Technical and Sentiment Overview
CREATE OR REPLACE VIEW v_daily_reliance_cockpit AS
SELECT 
    f.trade_date,
    f.close_price,
    f.vwap,
    f.rsi_14,
    s.technical_score,
    s.fundamental_score,
    s.news_score,
    s.composite_score,
    p.predicted_close,
    p.direction,
    p.signal
FROM reliance_features f
LEFT JOIN reliance_daily_scores s ON f.trade_date = s.trade_date
LEFT JOIN reliance_predictions p ON f.trade_date = p.trade_date;

-- 2. Rolling 30-Day Moving Averages & Volatility Summary
SELECT 
    trade_date,
    close_price,
    AVG(close_price) OVER (ORDER BY trade_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS sma_30,
    STDDEV(close_price) OVER (ORDER BY trade_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS vol_30
FROM raw_stock_prices
LIMIT 50;

-- 3. Top Bullish Correlation Days between News Sentiment and Returns
SELECT 
    p.trade_date,
    n.title,
    n.polarity_score,
    p.close_price,
    ROUND(((p.close_price - p.open_price) / p.open_price) * 100, 2) AS intraday_gain_pct
FROM raw_stock_prices p
JOIN raw_news_articles n ON p.trade_date = n.trade_date
WHERE n.polarity_score > 0.20
ORDER BY intraday_gain_pct DESC
LIMIT 10;
