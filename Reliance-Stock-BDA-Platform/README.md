# Reliance Industries (RELIANCE) — End-to-End Big Data Analytics (BDA) Stock Prediction Platform

A distributed Big Data Analytics platform designed to predict next-day closing prices and actionable trading signals (`STRONG BUY`, `BUY`, `HOLD`, `SELL`) for **Reliance Industries Limited (`RELIANCE.NS`)** by fusing:
1. **Kaggle Long-Term Historical OHLCV (2010 to 2025)**
2. **Financial News Sentiment with TextBlob NLP**
3. **Rolling Sector Momentum via Hadoop MapReduce**
4. **Streaming Broker Ticks & Real-Time Scoring via Kafka & Spark Streaming**
5. **Distributed Storage Lake via HDFS, Hive, and HBase**
6. **Machine Learning Pipeline via Spark MLlib (Random Forest & GBT Regressors)**
7. **Interactive 3-Page Presentation Cockpit via Streamlit & Plotly**

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                              │
│            Streamlit Multi-Page Cockpit (Port 8501)                    │
│   Page 1: Ingestion & Lake  │ Page 2: Indicators  │ Page 3: Prediction │
└──────────────────────────┬───────────────────────────┬─────────────────┘
                           │                           │
┌──────────────────────────┴───────────────────────────┴─────────────────┐
│                           SERVING LAYER                                │
│       Apache Hive (Warehousing)   │     Apache HBase (Fast Lookups)    │
│    Tables: reliance_prices,       │     Table: reliance_serving        │
│    features, scores, predictions  │     RowKey: RELIANCE#<rev_ts>      │
└──────────────────────────▲───────────────────────────▲─────────────────┘
                           │                           │
┌──────────────────────────┴───────────────────────────┴─────────────────┐
│                    PROCESSING & ANALYTICS LAYER                        │
│   Apache Pig (Batch ETL)  │ PySpark SQL (Window Indicators: EMA, VWAP) │
│   Hadoop MapReduce (30/60/90d) │ Spark Streaming (1-Min OHLCV Bars)    │
│   Spark MLlib Regression Pipeline (Time-Series Split: 70/15/15)        │
└──────────────────────────▲───────────────────────────▲─────────────────┘
                           │                           │
┌──────────────────────────┴───────────────────────────┴─────────────────┐
│                         STORAGE LAYER                                  │
│   HDFS 3-Zone Data Lake: /bda/lake/raw, /clean, /curated               │
│   Apache Kafka Topics: reliance-ticks, reliance-news                   │
└──────────────────────────▲───────────────────────────▲─────────────────┘
                           │                           │
┌──────────────────────────┴───────────────────────────┴─────────────────┐
│                        INGESTION LAYER                                 │
│   Kagglehub (Reliance 2010-2025) │ Curated Web News (TextBlob NLP)     │
│   Sector / NIFTY 50 Macro Feeds  │ Live Broker WebSocket Stub          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Directory Structure

```text
Reliance-Stock-BDA-Platform/
├── orchestrator.py                     # Master one-click pipeline runner
├── run_pipeline.bat                    # Windows execution runner
├── run_pipeline.sh                     # Linux / Docker execution runner
├── requirements.txt                    # Project dependencies
├── docker/
│   ├── Dockerfile                      # Hadoop 3.3.6, Spark 3.4.1, Hive, HBase
│   ├── docker-compose.yml              # Multi-container distributed stack
│   ├── entrypoint.sh                   # Cluster role initialization script
│   └── config/                         # core-site, hdfs-site, yarn-site, spark, hive, hbase
├── data/                               # Local data staging & cache
│   ├── raw/ (prices, news, sentiment)
│   ├── clean/ (joined dataset)
│   ├── curated/ (features, daily scores, momentum, predictions)
│   ├── models/ (model metrics JSON)
│   └── serving/ (HBase reverse timestamp cache)
├── module_1_storage/
│   ├── ingestion/
│   │   ├── kaggle_ingest.py            # Downloads Kaggle 2010-2025 dataset via kagglehub
│   │   ├── news_curated_feed.py        # 5 curated Reliance news items + TextBlob sentiment
│   │   ├── sector_nifty_sentiment.py   # Energy sector & NIFTY 50 macro parameters
│   │   ├── live_news_api_stub.py       # Moneycontrol / ET live RSS scraper
│   │   └── live_broker_feed_stub.py    # Broker WebSocket tick stream simulator
│   ├── hdfs/
│   │   ├── hdfs_lake_setup.sh          # Creates /raw, /clean, /curated in HDFS
│   │   └── upload_to_hdfs.py           # Synchronizes staged files to HDFS NameNode
│   ├── hive/
│   │   ├── hive_schema.hql             # DDL tables & partitions in reliance_bda_db
│   │   └── hive_queries.sql            # Materialized views & analytical queries
│   ├── hbase/
│   │   ├── hbase_setup.sh              # Creates table 'reliance_serving' (cf_tick, cf_score, cf_pred)
│   │   └── hbase_loader.py             # Reverse-timestamp row key generator RELIANCE#<rev_ts>
│   └── kafka/
│       ├── zookeeper_kafka_setup.sh    # Creates speed topics: reliance-ticks, reliance-news
│       └── kafka_producers.py          # High-velocity tick & news producer
├── module_2_processing/
│   ├── pig/
│   │   ├── etl_normalize_join.pig      # Apache Pig deduplication, date normalization, joins
│   │   └── run_pig_etl.py              # Runner with local standalone fallback
│   ├── mapreduce/
│   │   ├── sector_momentum_mapper.py   # Hadoop Streaming Mapper emitting (RELIANCE -> date,close,vol)
│   │   ├── sector_momentum_reducer.py  # Streaming Reducer computing 30d/60d/90d momentum
│   │   ├── run_mapreduce.sh            # Hadoop Streaming CLI runner
│   │   └── run_momentum_mr.py          # Local streaming pipe verifier
│   ├── spark/
│   │   ├── spark_feature_engineering.py# Spark SQL Window functions: EMA, VWAP, RSI, MACD, BB
│   │   └── spark_score_engine.py       # 4-Score engine (T, F, N, R -> Composite S)
│   ├── streaming/
│   │   └── spark_stream_live.py        # Spark Structured Streaming 1-min micro-batch bars
│   └── prediction/
│       ├── train_mllib_model.py        # MLlib Regression Pipeline with strict time-series split
│       └── predict_next_day.py         # Next-day price, confidence range & BUY/SELL signals
└── module_3_dashboard/
    ├── app.py                          # Streamlit application entrypoint & telemetry
    ├── data_loader.py                  # Resilient data binding provider
    ├── styles.py                       # Modern glassmorphism CSS design system
    └── pages/
        ├── 1_Pipeline_Ingestion.py     # Module 1 UI: BDA pipeline diagram & raw data inspect
        ├── 2_Technicals_Analytics.py   # Module 2 UI: Plotly Candlestick, EMA, VWAP, Gauges
        └── 3_Prediction_Decision.py    # Module 3 UI: Hero forecast, signal, drivers, backtest
```

---

## 🚀 Quickstart & Execution

### 1. Run the Entire End-to-End Pipeline in One Command
```bash
python orchestrator.py
```
*Executes Kaggle ingestion, news sentiment parsing, Pig deduplication, Hadoop MapReduce momentum, PySpark indicators, 4-factor scoring, MLlib model training, and next-day inference.*

### 2. Launch the Streamlit Interactive Dashboard
```bash
streamlit run module_3_dashboard/app.py
```
Open your browser at `http://localhost:8501`.

### 3. Running with Distributed Docker Cluster
```bash
cd docker
docker-compose up --build -d
```
Access cluster interfaces:
* **HDFS NameNode Web UI:** `http://localhost:9870`
* **Spark Master Web UI:** `http://localhost:8080`
* **YARN ResourceManager:** `http://localhost:8088`
* **HBase Master Web UI:** `http://localhost:16010`
* **Streamlit Dashboard:** `http://localhost:8501`

---

## 🧮 Mathematical Scoring & Prediction Model

### 1. Four Multi-Factor Scores (Each Scaled $0$ to $100$)
* **Technical Score ($T$):** Equal-weighted average of trend indicator signals (EMA 20/50 crossover, Close vs VWAP, RSI health, MACD histogram, Bollinger Band position, Volume surge).
* **Fundamental Score ($F$):** Evaluates Reliance Industries baseline metrics (P/E ratio, ROE, Debt/Equity, QoQ revenue growth).
* **News Score ($N$):** Exponential decay aggregation of TextBlob sentiment polarity $p \in [-1, 1]$ over the previous 3 trading sessions ($\lambda = 0.35$).
* **Real-Time Score ($R$):** Derived by Spark Streaming from live broker tick spreads and volume surges.
* **Composite Score ($S$):**
  $$S = 0.40 \cdot T + 0.20 \cdot F + 0.25 \cdot N + 0.15 \cdot R$$

### 2. Decision Logic
* **Predicted Return:** $r_{t+1} = \frac{S - 50}{50} \times 2.2\%$
* **Predicted Price:** $\hat{C}_{t+1} = C_t \times (1 + r_{t+1})$
* **Confidence Band:** $[\hat{C}_{t+1} - \text{MAE}, \hat{C}_{t+1} + \text{MAE}]$
* **Trade Signal:**
  * `STRONG BUY`: $S \ge 75$ and $r_{t+1} > 0$
  * `BUY`: $S \in [60, 75)$ and $r_{t+1} > 0$
  * `HOLD`: $S \in [40, 60)$
  * `SELL`: $S < 40$ or $r_{t+1} < -0.5\%$
