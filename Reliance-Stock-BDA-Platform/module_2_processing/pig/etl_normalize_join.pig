-- ============================================================================
-- etl_normalize_join.pig — Pig Latin Batch ETL for Reliance BDA Platform
-- ============================================================================
-- Loads raw prices and curated news from HDFS, deduplicates, normalizes types,
-- and executes a LEFT OUTER JOIN to produce the cleaned dataset.
-- Execution: pig -f module_2_processing/pig/etl_normalize_join.pig
-- ============================================================================

-- 1. Load Raw Prices
raw_prices = LOAD '/bda/lake/raw/prices/reliance_prices.csv'
    USING PigStorage(',')
    AS (
        trade_date:chararray,
        open_price:double,
        high_price:double,
        low_price:double,
        close_price:double,
        volume:long,
        ticker:chararray
    );

-- Skip header row
prices_no_header = FILTER raw_prices BY trade_date != 'Date';

-- Normalize Date & String fields
prices_normalized = FOREACH prices_no_header GENERATE
    SUBSTRING(trade_date, 0, 10) AS trade_date,
    (double) open_price AS open_price,
    (double) high_price AS high_price,
    (double) low_price AS low_price,
    (double) close_price AS close_price,
    (long) volume AS volume,
    UPPER(TRIM(ticker)) AS ticker;

-- Deduplicate by Date and Ticker
prices_grouped = GROUP prices_normalized BY (ticker, trade_date);
prices_deduped = FOREACH prices_grouped {
    sorted = ORDER prices_normalized BY volume DESC;
    top = LIMIT sorted 1;
    GENERATE FLATTEN(top);
};

-- 2. Load Raw Curated News
raw_news = LOAD '/bda/lake/raw/news/reliance_news.csv'
    USING PigStorage(',')
    AS (
        trade_date:chararray,
        source:chararray,
        title:chararray,
        summary:chararray,
        link:chararray,
        sentiment_label:chararray,
        polarity_score:double,
        subjectivity_score:double,
        ticker:chararray
    );

news_no_header = FILTER raw_news BY trade_date != 'trade_date';

news_normalized = FOREACH news_no_header GENERATE
    SUBSTRING(trade_date, 0, 10) AS trade_date,
    TRIM(source) AS source,
    TRIM(title) AS title,
    UPPER(TRIM(sentiment_label)) AS sentiment_label,
    (double) polarity_score AS polarity_score,
    UPPER(TRIM(ticker)) AS ticker;

-- Deduplicate news if multiple entries on same date
news_grouped = GROUP news_normalized BY (ticker, trade_date);
news_deduped = FOREACH news_grouped {
    top_news = LIMIT news_normalized 1;
    GENERATE FLATTEN(top_news);
};

-- 3. Left Outer Join: Prices with News on (trade_date, ticker)
joined_data = JOIN prices_deduped BY (trade_date, ticker) LEFT OUTER,
                   news_deduped BY (trade_date, ticker);

-- Project Clean Schema
clean_records = FOREACH joined_data GENERATE
    prices_deduped::trade_date AS trade_date,
    prices_deduped::open_price AS open_price,
    prices_deduped::high_price AS high_price,
    prices_deduped::low_price AS low_price,
    prices_deduped::close_price AS close_price,
    prices_deduped::volume AS volume,
    prices_deduped::ticker AS ticker,
    (news_deduped::polarity_score IS NOT NULL ? news_deduped::polarity_score : 0.0) AS news_polarity,
    (news_deduped::sentiment_label IS NOT NULL ? news_deduped::sentiment_label : 'NEUTRAL') AS sentiment_label;

-- 4. Store into HDFS Clean Zone
STORE clean_records INTO '/bda/lake/clean/reliance_daily_joined' USING PigStorage(',');
