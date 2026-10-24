# StockPulse — Distributed Big Data Analytics & Multi-Modal Stock Prediction Engine

> **CS404 · Big Data Analytics (BDA) Capstone Project** — National Stock Exchange (NSE) NIFTY 100 Universe

An enterprise Big Data Analytics platform predicting next-day stock price movements by fusing multi-source market information — historical OHLCV data, live broker ticks, financial news sentiment, and technical trading indicators — across a **7-container distributed Docker cluster**.

---

## 🎯 Key Highlights

| Metric                  | Value                           |
| ----------------------- | ------------------------------- |
| Total Processed Records | **6.85 Million+**               |
| Distributed Cluster     | **7-Container Docker Stack**    |
| Live Scoring Latency    | **Sub-2-Second**                |
| Pipeline Stages         | **5-Stage Multimodal**          |
| Historical Span         | **10 Years (2015–2025)**        |
| Universe                | **NIFTY 100 Equities (NSE)**    |
| Storage Compression     | **~78% (CSV → Snappy Parquet)** |
| Backtest Profit Factor  | **2.42**                        |
| Win/Loss Payoff Ratio   | **3.55 : 1**                    |

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                              │
│          StockPulse · Streamlit Multipage Dashboard (Port 8501)        │
│  Overview │ Pipeline & Data │ Technicals │ Prediction │ Backtest Replay│
└──────────────────────────┬───────────────────────────┬─────────────────┘
                           │                           │
┌──────────────────────────┴───────────────────────────┴─────────────────┐
│                           SERVING LAYER                                │
│       Apache Hive (Warehousing)   │     Apache HBase (Fast Lookups)    │
│    Tables: prices, features,      │     Table: stockpulse_serving      │
│    scores, predictions            │     RowKey: SYMBOL#<rev_ts>        │
└──────────────────────────▲───────────────────────────▲─────────────────┘
                           │                           │
┌──────────────────────────┴───────────────────────────┴─────────────────┐
│                    PROCESSING & ANALYTICS LAYER                        │
│   Apache Pig (Batch ETL)  │ PySpark SQL (Window Indicators: EMA, VWAP) │
│   Hadoop MapReduce (30/60/90d Momentum) │ Spark Streaming (1-Min Bars) │
│   Spark MLlib Regression Pipeline (Time-Series Split: 80/20)           │
└──────────────────────────▲───────────────────────────▲─────────────────┘
                           │                           │
┌──────────────────────────┴───────────────────────────┴─────────────────┐
│                         STORAGE LAYER                                  │
│   HDFS 3-Zone Data Lake: /stockpulse/lake/raw, /clean, /curated        │
│   Apache Kafka Topics: stock-ticks, stock-news                         │
└──────────────────────────▲───────────────────────────▲─────────────────┘
                           │                           │
┌──────────────────────────┴───────────────────────────┴─────────────────┐
│                        INGESTION LAYER                                 │
│  10-Year NIFTY 100 Historical OHLCV │ Curated News Feeds (TextBlob NLP)│
│  Sector / NIFTY Macro Sentiment     │ Live Broker WebSocket Tick Stub  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## � Technology Stack

### Distributed Storage

| Tool           | Version | Role                                                     |
| -------------- | ------- | -------------------------------------------------------- |
| Hadoop HDFS    | 3.3.6   | Fault-tolerant distributed file system (128 MB blocks)   |
| Apache Parquet | —       | Columnar storage with ~78% compression (Snappy codec)    |
| Apache Hive    | 2.3.2   | SQL warehouse over partitioned HDFS datasets             |
| Apache HBase   | 2.4     | Low-latency NoSQL serving store for scores & predictions |

### Distributed Processing

| Tool                   | Version | Role                                                      |
| ---------------------- | ------- | --------------------------------------------------------- |
| Apache Spark (PySpark) | 3.5     | In-memory Window analytics for technical indicators       |
| Apache Pig             | —       | Scriptable ETL for high-volume data joins & normalization |
| Hadoop MapReduce       | —       | Distributed batch aggregation for rolling sector momentum |

### Real-Time Streaming

| Tool                       | Version | Role                                                  |
| -------------------------- | ------- | ----------------------------------------------------- |
| Apache Kafka & ZooKeeper   | 3.7     | High-throughput event pub/sub for broker ticks & news |
| Spark Structured Streaming | 3.5     | 1-minute micro-batch OHLCV bar aggregation            |

### ML & Visualization

| Tool               | Role                                                 |
| ------------------ | ---------------------------------------------------- |
| Spark MLlib        | Distributed Random Forest & GBT regression pipelines |
| Streamlit & Plotly | Interactive analytics dashboard & trade replay       |

---

## 🖥️ Cluster Infrastructure

A **7-container Docker cluster** isolating storage, compute, streaming, and serving roles:

| Container                           | Endpoint           | Role                                                       |
| ----------------------------------- | ------------------ | ---------------------------------------------------------- |
| `hadoop-master` (NameNode)          | `:9870`            | HDFS namespace index & block metadata                      |
| `hadoop-datanode` (DataNode)        | `:9864`            | Physical 128 MB block storage                              |
| `spark-master`                      | `:8080`            | DAG execution, resource allocation                         |
| `spark-worker-1` & `spark-worker-2` | —                  | Distributed SQL transforms & MLlib training (4 cores each) |
| `kafka` (Broker + ZooKeeper)        | `:9092`            | High-velocity tick & news ingestion queue                  |
| `dashboard` (HBase + Streamlit)     | `:8501` / `:16010` | Serving layer & web UI                                     |

### HDFS Layout (`/stockpulse/lake`)

```
/raw          — Untouched incoming market ticks and raw news feeds
/clean        — Deduplicated, split-adjusted intermediate datasets
/curated      — Parquet tables with computed indicators and daily scores
/models       — Serialized MLlib models and performance metrics
/checkpoints  — Spark streaming recovery state offsets
```

---

## 📊 Dataset & Volume

| Source                                | Records        |
| ------------------------------------- | -------------- |
| Daily EOD OHLCV (NIFTY 100, 10 Years) | ~248,000       |
| Granular Intraday Tick Bars           | ~6,200,000     |
| Financial News & Sentiment Feed       | ~402,000       |
| **Total Ingested**                    | **~6,850,000** |

### Data Cleaning Audit

| Stage                                  | Count                          |
| -------------------------------------- | ------------------------------ |
| Raw Records Ingested                   | 6,850,000                      |
| Duplicate Records Removed              | 142,300                        |
| Imputed Records (LOCF / Sector Median) | 98,400                         |
| Clean Curated Records Produced         | 6,609,300                      |
| Storage Footprint                      | ~1.45 GB CSV → ~320 MB Parquet |
| Spark ETL Runtime                      | ~84 seconds (4 cores)          |

---

## �📁 Project Directory Structure

```text
Reliance-Stock-BDA-Platform/
├── orchestrator.py                     # Master one-click pipeline runner
├── run_pipeline.bat                    # Windows execution runner
├── run_pipeline.sh                     # Linux / Docker execution runner
├── requirements.txt                    # Project dependencies
├── docker/
│   ├── Dockerfile                      # Hadoop 3.3.6, Spark 3.5, Hive, HBase
│   ├── docker-compose.yml              # 7-container distributed stack
│   ├── entrypoint.sh                   # Cluster role initialization script
│   └── config/                         # core-site, hdfs-site, yarn-site, spark, hive, hbase
├── data/
│   ├── raw/     (prices, news, sentiment)
│   ├── clean/   (joined dataset)
│   ├── curated/ (features, daily scores, momentum, predictions)
│   ├── models/  (model metrics JSON)
│   └── serving/ (HBase reverse-timestamp cache)
├── module_1_storage/
│   ├── ingestion/
│   │   ├── kaggle_ingest.py            # Downloads NIFTY 100 10-year dataset via kagglehub
│   │   ├── news_curated_feed.py        # Curated financial news + TextBlob sentiment
│   │   ├── sector_nifty_sentiment.py   # Energy sector & NIFTY macro parameters
│   │   ├── live_news_api_stub.py       # Moneycontrol / ET live RSS scraper stub
│   │   └── live_broker_feed_stub.py    # Broker WebSocket tick stream simulator
│   ├── hdfs/
│   │   ├── hdfs_lake_setup.sh          # Creates /raw, /clean, /curated in HDFS
│   │   └── upload_to_hdfs.py           # Synchronizes staged files to HDFS NameNode
│   ├── hive/
│   │   ├── hive_schema.hql             # DDL tables & partitions
│   │   └── hive_queries.sql            # Materialized views & analytical queries
│   ├── hbase/
│   │   ├── hbase_setup.sh              # Creates serving table (cf_tick, cf_score, cf_pred)
│   │   └── hbase_loader.py             # Reverse-timestamp row key: SYMBOL#<rev_ts>
│   └── kafka/
│       ├── zookeeper_kafka_setup.sh    # Creates speed topics: stock-ticks, stock-news
│       └── kafka_producers.py          # High-velocity tick & news producer
├── module_2_processing/
│   ├── pig/
│   │   ├── etl_normalize_join.pig      # Apache Pig deduplication, date normalization, joins
│   │   └── run_pig_etl.py              # Runner with local standalone fallback
│   ├── mapreduce/
│   │   ├── sector_momentum_mapper.py   # Hadoop Streaming Mapper
│   │   ├── sector_momentum_reducer.py  # Reducer computing 30d/60d/90d momentum
│   │   ├── run_mapreduce.sh            # Hadoop Streaming CLI runner
│   │   └── run_momentum_mr.py          # Local streaming pipe verifier
│   ├── spark/
│   │   ├── spark_feature_engineering.py# Spark SQL Window: EMA, VWAP, RSI, MACD, BB
│   │   └── spark_score_engine.py       # 4-Score engine (T, F, N, R → Composite S)
│   ├── streaming/
│   │   └── spark_stream_live.py        # Spark Structured Streaming 1-min micro-batch
│   └── prediction/
│       ├── train_mllib_model.py        # MLlib Pipeline with strict 80/20 time-series split
│       └── predict_next_day.py         # Next-day price, confidence range & trade signals
└── module_3_dashboard/
    ├── app.py                          # Entrypoint: page config, navigation, sidebar, ticker
    ├── theme.py                        # Design tokens, CSS, Plotly template, logo SVG
    ├── components.py                   # Reusable UI helpers (tiles, badges, gauge, fan chart)
    ├── data_loader.py                  # Data provider, file metadata, source detection
    ├── simulator_engine.py             # Backtest computations
    ├── styles.py                       # Backward-compatible shim re-exporting theme CSS
    ├── assets/                         # SVG favicon and wordmark
    ├── docs/                           # Design brief, parity checklist, mockup, screenshots
    └── pages/
        ├── 0_Overview.py               # Last close, tomorrow's call, composite gauge, news
        ├── 1_Pipeline_Ingestion.py     # Stage status, data quality, HDFS / Hive inspectors
        ├── 2_Technicals_Analytics.py   # Price chart, RSI / MACD, indicator summary, calendar
        ├── 3_Prediction_Decision.py    # Forecast, signal rules, model card, feature importances
        └── 4_Backtest_Simulator.py     # Day-by-day replay, equity curve, trade ledger
```

---

## 🧮 Mathematical Scoring & Prediction Model

### Multi-Factor Score Engine (Each Score Scaled 0–100)

| Score                | Formula / Source                                                                                          | Weight  |
| -------------------- | --------------------------------------------------------------------------------------------------------- | ------- |
| Technical ($T$)      | Equal-weight avg of 6 indicators: EMA cross, VWAP, RSI, MACD, Bollinger %B, Volume Surge                  | **40%** |
| Fundamental ($F$)    | P/E percentile, ROE, Debt/Equity, QoQ revenue growth                                                      | **20%** |
| News Sentiment ($N$) | TextBlob polarity with 3-day exp-decay ($\lambda = 0.35$): $\tilde{N}_t = 0.35 N_t + 0.65\tilde{N}_{t-1}$ | **25%** |
| Real-Time ($R$)      | Spark Streaming intraday return scaled by tick volume surge                                               | **15%** |

$$\boxed{S = 0.40 \cdot T + 0.20 \cdot F + 0.25 \cdot N + 0.15 \cdot R}$$

### Technical Indicators

| Indicator            | Parameters            | Purpose                                      |
| -------------------- | --------------------- | -------------------------------------------- |
| Dual EMA             | 20-period & 50-period | Golden/death cross & trend direction         |
| VWAP                 | Daily                 | Institutional fair-value benchmark           |
| RSI                  | 14-period             | Overbought (>70) / Oversold (<30) zones      |
| MACD                 | 12, 26, 9             | Momentum speed & directional acceleration    |
| Bollinger Bands (%B) | 20-period, 2σ         | Volatility expansion & breakout              |
| Volume Surge Ratio   | 20-day avg baseline   | Validates breakouts with volume confirmation |

### Prediction & Decision Logic

$$r_{t+1} = \frac{S - 50.0}{50.0} \times 2.2\%$$

$$\hat{C}_{t+1} = C_t \times (1 + r_{t+1})$$

$$\text{Confidence} = \text{clip}\!\left(50.0 + 0.8 \cdot |S - 50.0|,\ 55\%,\ 92\%\right)$$

| Signal       | Condition                         |
| ------------ | --------------------------------- |
| `STRONG BUY` | $S \ge 75$ and $r_{t+1} > 0$      |
| `BUY`        | $60 \le S < 75$ and $r_{t+1} > 0$ |
| `HOLD`       | $40 \le S < 60$                   |
| `SELL`       | $S < 40$ or $r_{t+1} < -0.5\%$    |

---

## 🤖 Machine Learning Model

**Primary Model:** Random Forest Regressor (Spark MLlib Pipeline)
**Benchmark:** Gradient-Boosted Trees (GBT) + Naive Persistence Baseline ($\hat{C}_{t+1} = C_t$)

### Hyperparameters

| Parameter               | Value                                                 |
| ----------------------- | ----------------------------------------------------- |
| `numTrees`              | 100                                                   |
| `maxDepth`              | 8                                                     |
| `subsamplingRate`       | 0.80                                                  |
| `featureSubsetStrategy` | `auto` ($\sqrt{d}$ per split)                         |
| `minInstancesPerNode`   | 5                                                     |
| Train / Test Split      | 80% (2015–2023) / 20% (2024–2025) — strict time order |

### Top Feature Importances

| Feature                  | Importance |
| ------------------------ | ---------- |
| 30-Day Momentum          | 13.6%      |
| Volume Surge Ratio       | 12.7%      |
| Real-Time Intraday Score | 12.3%      |
| MACD Histogram           | 10.9%      |

---

## 📈 Backtest Performance

Walk-forward out-of-sample simulation on unseen 2024–2025 data. Starting capital: ₹100,000.

| Metric                                      | Value                      |
| ------------------------------------------- | -------------------------- |
| Directional Accuracy                        | 50.64% – 51.40%            |
| High-Conviction Win Rate (Confidence ≥ 70%) | **57.14%** (4W / 3L)       |
| Average Win                                 | +1.35% (+₹1,490 per trade) |
| Average Loss                                | -0.38% (-₹382 per trade)   |
| Win/Loss Payoff Ratio                       | **3.55 : 1**               |
| Profit Factor                               | **2.42**                   |
| Maximum Drawdown                            | **-3.2%**                  |

**Risk Management Rules:**

- Entry only on `BUY` / `STRONG BUY` with model confidence ≥ 60%
- Hard stop-loss at **-1.2%** from entry price
- Trailing take-profit above **+2.4%** (1:2 risk-to-reward)
- 100% cash position during `HOLD` / `SELL` regimes

---

## 🚀 Quickstart

### 1. Run Everything in One Command (Recommended)

```bash
python run.py
```

This executes the full pipeline (ingestion → Pig ETL → MapReduce → Spark → MLlib training) and opens the dashboard at `http://localhost:8501`.

### 2. Partial Execution

```bash
# Pipeline only (no UI)
python run.py --pipeline-only

# Dashboard only (uses cached artifacts)
python run.py --dashboard-only
```

### 3. Distributed Docker Cluster

```bash
cd docker
docker-compose up --build -d
```

| Interface            | URL                      |
| -------------------- | ------------------------ |
| HDFS NameNode        | `http://localhost:9870`  |
| Spark Master         | `http://localhost:8080`  |
| YARN ResourceManager | `http://localhost:8088`  |
| HBase Master         | `http://localhost:16010` |
| StockPulse Dashboard | `http://localhost:8501`  |

---

## 🔗 Project Resources

| Resource             | Link                                                                                                                                                      |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 📽️ Demo Video        | [Google Drive](https://drive.google.com/file/d/1s5VqGVlbkMA3KXdryaGd1MESbOuFep62/view?usp=sharing)                                                        |
| 💻 GitHub Repository | [ajax-39/Stock-Pulse](https://github.com/ajax-39/Stock-Pulse.git)                                                                                         |
| 📦 Dataset (Kaggle)  | [NIFTY 50 Stocks — 1-Min Intraday Data](https://www.kaggle.com/datasets/debashis74017/stock-market-data-nifty-50-stocks-1-min-data?select=ABB_minute.csv) |

---

## 📚 Academic References

| Reference                                                                                        | Link                                                 | Key Takeaway                                                                                                       |
| ------------------------------------------------------------------------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Khaidem et al. (2016) — _"Predicting the direction of stock market prices using Random Forest"_  | [arXiv:1605.00003](https://arxiv.org/abs/1605.00003) | Random Forest captures non-linear technical indicator signals while resisting market noise                         |
| Chen et al. (2024, SARF) — _"Stock Price Prediction using Sentiment Analysis and Random Forest"_ | [arXiv:2403.02381](https://arxiv.org/abs/2403.02381) | Exponential-decay NLP sentiment augmentation significantly improves predictive accuracy over pure technical models |

---

## 👥 Contributors

| Name                 | ID            | Contribution                                                                                                                                                      |
| -------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Aditya Medhane**   | `2023BCS-003` | Project overview & pipeline architecture, Big Data tools & tech stack, NIFTY 100 dataset curation & 6.85M volume quantification                                   |
| **Atharv Jagzap**    | `2023BCS-012` | Multi-source scoring engine & academic literature, Spark MLlib model training & hyperparameter tuning, technical trading indicators, final score & decision logic |
| **Amogh Deshpande**  | `2023BCS-018` | Backtest simulator methodology & execution setup, performance metrics & statistical validation, day-by-day trade replay & Streamlit dashboard integration         |
| **Vishwas Kulkarni** | `2023BCS-072` | 7-container Docker cluster & HDFS architecture, Spark ETL & Pig data cleaning (6.85M records), analytics & multi-source signal integration                        |

---

_StockPulse · CS404 Big Data Analytics Capstone · 2025_
