-- ============================================================================
-- hive_schema.hql — Hive Data Warehouse Schema Definitions for Reliance BDA
-- Execution: hive -f module_1_storage/hive/hive_schema.hql
-- ============================================================================

CREATE DATABASE IF NOT EXISTS reliance_bda_db;
USE reliance_bda_db;

-- ----------------------------------------------------------------------------
-- 1. Raw Stock Prices Table (External mapping to HDFS Raw Zone)
-- ----------------------------------------------------------------------------
CREATE EXTERNAL TABLE IF NOT EXISTS raw_stock_prices (
    trade_date      STRING,
    open_price      DOUBLE,
    high_price      DOUBLE,
    low_price       DOUBLE,
    close_price     DOUBLE,
    volume          BIGINT,
    ticker          STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/bda/lake/raw/prices'
TBLPROPERTIES ('skip.header.line.count'='1');

-- ----------------------------------------------------------------------------
-- 2. Raw News Articles Table (External mapping to HDFS Raw News Zone)
-- ----------------------------------------------------------------------------
CREATE EXTERNAL TABLE IF NOT EXISTS raw_news_articles (
    trade_date          STRING,
    source              STRING,
    title               STRING,
    summary             STRING,
    link                STRING,
    sentiment_label     STRING,
    polarity_score      DOUBLE,
    subjectivity_score  DOUBLE,
    ticker              STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/bda/lake/raw/news'
TBLPROPERTIES ('skip.header.line.count'='1');

-- ----------------------------------------------------------------------------
-- 3. Raw Market & Sector Sentiment Table
-- ----------------------------------------------------------------------------
CREATE EXTERNAL TABLE IF NOT EXISTS raw_market_sentiment (
    trade_date              STRING,
    sector                  STRING,
    sector_pe_ratio         DOUBLE,
    sector_momentum_score   DOUBLE,
    nifty50_sentiment_label STRING,
    nifty50_sentiment_score DOUBLE,
    india_vix               DOUBLE,
    brent_crude_usd         DOUBLE,
    fii_dii_net_flow_cr     DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/bda/lake/raw/sentiment'
TBLPROPERTIES ('skip.header.line.count'='1');

-- ----------------------------------------------------------------------------
-- 4. Clean & Joined Daily Feature Store (Partitioned by Year and Month)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reliance_features (
    trade_date          STRING,
    close_price         DOUBLE,
    open_price          DOUBLE,
    high_price          DOUBLE,
    low_price           DOUBLE,
    volume              BIGINT,
    ema_20              DOUBLE,
    ema_50              DOUBLE,
    vwap                DOUBLE,
    rsi_14              DOUBLE,
    macd                DOUBLE,
    macd_signal         DOUBLE,
    macd_hist           DOUBLE,
    bb_upper            DOUBLE,
    bb_lower            DOUBLE,
    bb_pos              DOUBLE,
    volume_ratio        DOUBLE,
    daily_return        DOUBLE,
    momentum_30d        DOUBLE,
    news_sentiment      DOUBLE
)
PARTITIONED BY (year STRING, month STRING)
STORED AS ORC
LOCATION '/bda/lake/curated/reliance_features';

-- ----------------------------------------------------------------------------
-- 5. Multi-Factor Daily Scores Store
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reliance_daily_scores (
    trade_date          STRING,
    technical_score     DOUBLE,
    fundamental_score   DOUBLE,
    news_score          DOUBLE,
    realtime_score      DOUBLE,
    composite_score     DOUBLE,
    dominant_factor     STRING,
    computed_at         STRING
)
STORED AS ORC
LOCATION '/bda/lake/curated/reliance_scores';

-- ----------------------------------------------------------------------------
-- 6. Predictions & Signals History Store
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reliance_predictions (
    trade_date          STRING,
    actual_close        DOUBLE,
    predicted_close     DOUBLE,
    predicted_return    DOUBLE,
    lower_bound         DOUBLE,
    upper_bound         DOUBLE,
    direction           STRING,   -- UP / DOWN / FLAT
    signal              STRING,   -- STRONG BUY / BUY / HOLD / SELL
    confidence          DOUBLE,
    created_at          STRING
)
STORED AS ORC
LOCATION '/bda/lake/curated/reliance_predictions';
