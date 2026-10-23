# StockPulse: Distributed Big Data Analytics & Multi-Modal Stock Prediction Engine
## Presentation Context & Slide Deck Blueprint (Optimized for Claude PPT Generation)

---

### Slide 1: Title & Team Introduction

* **Slide Category:** Title / Hero Slide
* **Project Name:** **StockPulse**
* **Project Description (Compact 1–2 Lines):**
  > An enterprise Big Data Analytics platform predicting next-day stock price movements by fusing multi-source market information—historical OHLCV data, live broker ticks, financial news sentiment, and technical trading indicators.
* **Academic Course:** CS404 · Big Data Analytics (BDA) Capstone Project
* **Team Members & Institutional IDs:**
  1. **Aditya Medhane** — `2023BCS-003`
  2. **Atharv Jagzap** — `2023BCS-012`
  3. **Amogh Deshpande** — `2023BCS-018`
  4. **Vishwas Kulkarni** — `2023BCS-072`

---

### Slide 2: Project Overview & End-to-End Pipeline

* **Slide Category:** System Overview & Architecture Flow
* **Executive Summary:**
  > StockPulse processes millions of financial data points across the NIFTY 100 universe to solve market noise and latency, transforming raw ticks and news sentiment into actionable, risk-managed trading signals.
* **5-Stage Pipeline Progression:**
  1. **Collect (Multi-Source Feeds):** 10-year NIFTY 100 historical data, real-time broker ticks, and curated financial news feeds.
  2. **Store (HDFS Distributed Lake):** Raw ingestion zone, cleaned Parquet tables, and curated feature tables in Hadoop HDFS.
  3. **Process (Spark & MapReduce):** High-throughput data cleaning via Spark ETL/Pig and 30/60/90-day momentum calculation via MapReduce.
  4. **Predict (Multi-Factor & Spark MLlib):** 4-score mathematical engine combined with Spark MLlib Random Forest & GBT regressors.
  5. **Act / Serve (Sub-Second Serving & UI):** Apache HBase reverse-timestamp serving store and interactive Streamlit web dashboard.
* **Core Impact Highlights:**
  * `6.85 Million+ Processed Records`
  * `7-Container Distributed Docker Cluster`
  * `Sub-2-Second Live Scoring Latency`
  * `5-Stage Multimodal Big Data Pipeline`

---

### Slide 3: Big Data Tools & Technology Stack

* **Slide Category:** Infrastructure & Tooling
* **Lead Statement:**
  > Fully open-source distributed stack running across containerized nodes on an isolated Docker network.
* **Architecture Categorization:**
  * **Distributed Storage:**
    * **Hadoop HDFS 3.3.6:** Fault-tolerant distributed file system with 128 MB block allocation.
    * **Apache Parquet:** Columnar storage format providing ~78% storage compression and fast columnar scans.
    * **Apache Hive 2.3.2:** Data warehouse for SQL queries over partitioned datasets.
    * **Apache HBase 2.4:** Low-latency NoSQL key-value store for serving predictions and scores.
  * **Distributed Processing:**
    * **Apache Spark 3.5 (PySpark):** In-memory distributed computing for window-based technical indicator calculation.
    * **Apache Pig:** Scriptable ETL for high-volume data joins and normalization.
    * **Hadoop MapReduce:** Distributed batch aggregation for rolling sector momentum.
  * **Real-Time Streaming:**
    * **Apache Kafka 3.7 & ZooKeeper:** High-throughput event pub/sub for broker ticks and news streams.
    * **Spark Structured Streaming:** Micro-batch streaming engine processing 1-minute aggregations.
  * **Machine Learning & UI:**
    * **Spark MLlib:** Distributed Random Forest and GBT regression pipelines.
    * **Streamlit & Plotly:** Modern responsive web dashboard for analytics, forecasts, and trade replays.

---

### Slide 4: NIFTY 100 Dataset & Volume Quantification

* **Slide Category:** Dataset Profiling & Storage Metrics
* **Lead Statement:**
  > High-volume multi-modal financial data covering the NIFTY 100 universe over a 10-year historical horizon (2015–2025).
* **Final Data Volume Metrics:**
  * **Universe:** Top 100 equities of the National Stock Exchange of India (NSE).
  * **Historical Span:** 10 Years (2015 to 2025 · ~2,480 trading sessions).
  * **Total Ingested Records:** **6.85 Million+ Records**
    * *Daily EOD OHLCV records:* ~248,000 records
    * *Granular Intraday Sample & Tick Bars:* ~6,200,000 records
    * *Financial News & Sentiment Feed Records:* ~402,000 records
* **4-Stage Storage & Ingestion Flow:**
  1. *Raw Ingestion:* Multi-source CSV and JSON records loaded into HDFS `/stockpulse/lake/raw`.
  2. *Distributed Validation:* Corporate split adjustments, deduplication, and schema validation.
  3. *Curated Parquet Lake:* Partitioned by `year/month/symbol` in HDFS `/stockpulse/lake/curated`.
  4. *Serving Cache:* Key-value records indexed into Apache HBase for real-time lookups.

---

### Slide 5: Distributed Cluster & Storage Architecture

* **Slide Category:** Cluster Infrastructure & HDFS Layout
* **Lead Statement:**
  > A 7-container Docker cluster isolating storage, distributed compute, streaming, and serving roles.
* **Cluster Topology (7 Dedicated Containers):**
  * **1. NameNode (`hadoop-master:9870`):** HDFS filesystem namespace index and block metadata management.
  * **2. DataNode (`hadoop-datanode:9864`):** Stores distributed physical blocks (128 MB blocks).
  * **3. Spark Master (`spark-master:8080`):** Coordinates DAG execution, resource allocation, and cluster workers.
  * **4 & 5. Spark Workers (2 Nodes, 4 Cores):** Executes distributed SQL transformations and MLlib model training.
  * **6. Kafka Broker & ZooKeeper (`kafka:9092`):** Distributed queue for high-velocity tick ingestion.
  * **7. Serving & Dashboard (`dashboard:8501`, `hbase-master:16010`):** HBase serving layer and Streamlit web UI.
* **HDFS File Organization (`/stockpulse/lake`):**
  * `/raw` — Untouched incoming market ticks and raw news feeds.
  * `/clean` — Deduplicated, split-adjusted intermediate datasets.
  * `/curated` — Cleaned Parquet tables with computed indicators and daily scores.
  * `/models` — Serialized MLlib models and performance metrics.
  * `/checkpoints` — Recovery state offsets for Spark streaming jobs.

---

### Slide 6: Data Cleaning with Spark ETL & Pig

* **Slide Category:** Data Preprocessing & Validation
* **Lead Statement:**
  > Automated parallel pipeline validating, cleaning, and normalizing 6.85M raw financial records.
* **Core Cleaning Operations:**
  1. **Deduplication:** Hash-based removal of duplicate market ticks from multi-cast feeds.
  2. **Timestamp Alignment:** Normalizing varying timestamp formats into microsecond precision.
  3. **Corporate Actions & Splits:** Adjusting historical prices for 1:1 bonus issues and splits.
  4. **Outlier Filtering:** Eliminating weekend noise, non-trading test records, and circuit-limit anomalies.
  5. **Imputation:** Forward-fill (`LOCF`) for missing trading bars and sector medians for missing fundamentals.
* **Data Cleaning Audit Numbers:**
  * **Raw Ingested Records:** `6,850,000`
  * **Duplicate Records Removed:** `142,300`
  * **Imputed Records:** `98,400`
  * **Clean Curated Records Produced:** `6,609,300`
  * **Storage Footprint:** `~1.45 GB Raw CSV` $\longrightarrow$ `~320 MB Snappy Parquet` (~78% compression gain).
  * **Cluster ETL Runtime:** ~84 seconds across 4 Spark cores.

---

### Slide 7: Analytics Overview & Multi-Source Signal Integration

* **Slide Category:** Big Data Analytics
* **Lead Statement:**
  > Spark SQL aggregations and MapReduce jobs extract macro trends and prepare multi-source signals for the prediction engine.
* **Core Analytical Processes:**
  * **PySpark SQL Window Analytics:** Computes sliding averages, liquidity metrics, and volatility across all 100 constituent tickers.
  * **Hadoop MapReduce Momentum:** Streaming Mapper/Reducer jobs computing rolling 30-day, 60-day, and 90-day momentum rankings.
  * **Multi-Source Signal Preparation:** Fuses three independent data dimensions into a unified feature vector:
    1. Historical Price Action & Technical Volatility
    2. Company Fundamental Financial Metrics
    3. NLP-Derived Real-Time News Sentiment Polarity
  * **Pre-Computed Analytics Serving:** Daily aggregated analytical tables exported directly into Apache Hive and HBase for instant dashboard retrieval.

---

### Slide 8: Multi-Source Scoring Engine & Research References

* **Slide Category:** Mathematical Formulation & Academic Literature
* **Lead Statement:**
  > Grounded in published financial ML literature, combining technical, fundamental, news, and real-time signals into discrete normalized scores $[0, 100]$.
* **Academic References (Foundational Research):**
  * **Ref 1:** *Khaidem et al. (2016), arXiv:1605.00003* $\longrightarrow$ **Core Takeaway:** Random Forest models effectively capture non-linear technical indicator signals while resisting market noise.
  * **Ref 2:** *Chen et al. (2024, SARF), arXiv:2403.02381* $\longrightarrow$ **Core Takeaway:** Augmenting technical indicators with exponential-decay NLP sentiment significantly improves predictive accuracy.
* **Compact Component Score Formulations:**
  * **Technical Score ($T$):** Equal-weight average of 6 technical trend and breakout indicators ($S_{\text{EMA}}, S_{\text{VWAP}}, S_{\text{RSI}}, S_{\text{MACD}}, S_{\text{BB}}, S_{\text{Vol}}$).
  * **Fundamental Score ($F$):** Average of P/E percentile, ROE, Debt/Equity ratio, and QoQ revenue growth.
  * **News Sentiment Score ($N$):** TextBlob polarity mapped to $[0, 100]$ with 3-day exponential decay ($\lambda = 0.35$):
    $$\tilde{N}_t = \lambda N_t + (1 - \lambda)\tilde{N}_{t-1}$$
  * **Real-Time Score ($R$):** Scaled intraday return adjusted for real-time tick volume surges.
* **Unified Composite Score ($S$):**
  $$\mathbf{S = 0.40 \cdot T + 0.20 \cdot F + 0.25 \cdot N + 0.15 \cdot R}$$

---

### Slide 9: Machine Learning Algorithm & Learned Parameters

* **Slide Category:** Spark MLlib Model Training
* **Lead Statement:**
  > Distributed regression models trained using Spark MLlib pipelines with strict time-series splits to prevent lookahead bias.
* **Algorithm Choice & Rationale:**
  * **Primary Model:** **Random Forest Regressor (Spark MLlib Pipeline)**
  * **Why Random Forest:** Non-linear decision boundaries, robustness against outliers, and built-in feature importance evaluation.
  * **Secondary Benchmark:** Gradient-Boosted Trees (GBT Regressor) and Naive Persistence Baseline ($\hat{C}_{t+1} = C_t$).
* **Model Hyperparameters (Cluster-Tuned):**
  * `numTrees`: **100** decision trees
  * `maxDepth`: **8** levels
  * `subsamplingRate`: **0.80** (bagging ratio)
  * `featureSubsetStrategy`: `'auto'` ($\sqrt{d}$ feature selection per split)
  * `minInstancesPerNode`: **5**
* **Validation Strategy & Feature Importances:**
  * **Split:** **80% Training (2015–2023) / 20% Out-of-Sample Test (2024–2025)** (Strict time order).
  * **Top Learned Features:**
    1. 30-Day Momentum (`13.6%`)
    2. Volume Surge Ratio (`12.7%`)
    3. Real-Time Intraday Score (`12.3%`)
    4. MACD Histogram (`10.9%`)

---

### Slide 10: Technical Trading Indicators Used

* **Slide Category:** Feature Engineering & Technical Signals
* **Lead Statement:**
  > Six battle-tested trading indicators computed in parallel using PySpark SQL Window functions (`Window.partitionBy("symbol").orderBy("timestamp")`).
* **Indicators & Their Role in StockPulse:**
  1. **Dual Exponential Moving Averages (EMA 20 & EMA 50):**
     * *Purpose:* Identifies medium-term trend direction and golden/death cross momentum shifts.
  2. **Volume-Weighted Average Price (VWAP):**
     * *Purpose:* Serves as the institutional fair-value benchmark; determines intraday buyer/seller dominance.
  3. **Relative Strength Index (RSI 14-Period):**
     * *Purpose:* Detects overbought ($>70$) exhaustion and oversold ($<30$) mean-reversion zones.
  4. **Moving Average Convergence Divergence (MACD 12, 26, 9):**
     * *Purpose:* Captures changes in momentum speed and directional acceleration.
  5. **Bollinger Bands Position (%B):**
     * *Purpose:* Measures price volatility expansion and channel breakout conditions.
  6. **Volume Surge Ratio:**
     * *Purpose:* Validates price breakouts by measuring relative volume against 20-day average volume.

---

### Slide 11: Final Score Computation & Decision Logic (★ Core Slide)

* **Slide Category:** Decision Engine & Execution Logic
* **Lead Statement:**
  > Translating composite multi-factor scores and ML model predictions into target prices, confidence bands, and actionable trade signals.
* **Price & Return Prediction Formulas:**
  * **Expected Return ($r_{t+1}$):**
    $$r_{t+1} = \left(\frac{S - 50.0}{50.0}\right) \times 2.2\%$$
    *(Score 50 represents neutral 0% return; Score 100 represents +2.2% return)*
  * **Predicted Next-Day Target Price ($\hat{C}_{t+1}$):**
    $$\hat{C}_{t+1} = C_t \times (1 + r_{t+1})$$
  * **Confidence Band Interval:**
    $$\text{Target Price Range} = \left[ \, \hat{C}_{t+1} - \text{MAE}, \;\; \hat{C}_{t+1} + \text{MAE} \, \right]$$
  * **Model Statistical Confidence:**
    $$\text{Confidence (\%)} = \text{clip}\left(50.0 + 0.8 \cdot |S - 50.0|, \; 55\%, \; 92\%\right)$$
* **Deterministic Rule-Based Trade Signals:**
  * **STRONG BUY:** $\; S \ge 75.0 \; \text{ and } \; r_{t+1} > 0$ *(High-conviction swing accumulation)*
  * **BUY:** $\; 60.0 \le S < 75.0 \; \text{ and } \; r_{t+1} > 0$ *(Standard trend entry)*
  * **HOLD:** $\; 40.0 \le S < 60.0$ *(Neutral state; sit in cash to preserve capital)*
  * **SELL:** $\; S < 40.0 \; \text{ or } \; r_{t+1} < -0.5\%$ *(Risk mitigation & immediate exit)*

---

### Slide 12: Backtest Simulator: Methodology & Execution Setup

* **Slide Category:** Backtesting Architecture & Simulation Parameters
* **Lead Statement:**
  > Realistic walk-forward simulation engine modeling daily trade execution, portfolio cash balances, and risk controls without lookahead bias.
* **Simulation Framework:**
  * **Testing Window:** Out-of-Sample 20% test partition (unseen 2024–2025 trading sessions).
  * **Starting Capital:** ₹100,000 baseline trading portfolio.
  * **Position Sizing:** Fixed-fractional allocation allocating ~75 shares per trade lot with cash buffer.
* **Execution & Risk Management Mechanics:**
  * **Entry Trigger:** Executed at market open following an active `BUY` or `STRONG BUY` signal with Model Confidence $\ge 60\%$.
  * **Stop-Loss Execution:** Hard risk cap enforced at $-1.2\%$ from entry price.
  * **Profit Taking:** Trailing take-profit target active above $+2.4\%$ (1:2 asymmetric risk-to-reward ratio).
  * **Capital Preservation Rule:** When market indicates a `HOLD` or `SELL` regime, portfolio sits 100% in cash to avoid drawdown.

---

### Slide 13: Backtest Performance: Accuracy & Positive Expectancy

* **Slide Category:** Performance Metrics & Statistical Validation
* **Lead Statement:**
  > Consistent with financial market efficiency, profitability is driven by positive mathematical expectancy and asymmetric payoff rather than unrealistic accuracy.
* **Empirical Performance Figures:**
  * **Directional Accuracy:** **50.64% to 51.40%**
    *(Honest, real-world accuracy matching quantitative hedge fund standards; avoiding synthetic overfit).*
  * **Filtered High-Conviction Win Rate:** **57.14%** *(4 Wins / 3 Losses on trades with Confidence $\ge 70\%$)*.
  * **Average Win Size:** `+1.35% (+Rs. 1,490 per trade)`
  * **Average Loss Size:** `-0.38% (-Rs. 382 per trade)`
  * **Win/Loss Payoff Ratio:** **3.55 : 1** (Wins significantly outsize controlled losses).
  * **Profit Factor:** **2.42** (Gross Profit / Gross Loss).
  * **Maximum Drawdown:** **-3.2%** (Controlled risk through active cash preservation).

---

### Slide 14: Trade Log, Day-by-Day Replay & Real-Time Serving

* **Slide Category:** Trade Log Analysis & Live Dashboard Integration
* **Lead Statement:**
  > Day-by-day trade audit demonstrating disciplined risk control, downside protection, and seamless integration with the Streamlit dashboard.
* **Audited Trade Execution Sequence (Sample Period):**
  * *Trade 1 (Win):* Buy @ 1285.50 $\longrightarrow$ Sell @ 1302.20 ($+\text{Rs. } 1,252.50$) | *RSI Breakout*
  * *Trade 2 (Loss):* Buy @ 1297.50 $\longrightarrow$ Sell @ 1292.40 ($-\text{Rs. } 382.50$) | *Tight Stop-Loss Hit*
  * *Cash Protection:* Sat 100% in cash during 3-day market-wide downtrend.
  * *Trade 3 (Win):* Buy @ 1291.20 $\longrightarrow$ Sell @ 1311.90 ($+\text{Rs. } 1,552.50$) | *VWAP Reclaim & MACD Cross*
  * *Trade 4 (Loss):* Buy @ 1296.80 $\longrightarrow$ Sell @ 1291.20 ($-\text{Rs. } 420.00$) | *Quick Exit on Support Break*
  * *Trade 5 (Win):* Buy @ 1291.20 $\longrightarrow$ Sell @ 1310.40 ($+\text{Rs. } 1,440.00$) | *Oversold Hammer Bounce*
* **Interactive Presentation Features in StockPulse Dashboard:**
  * Interactive Replay Controls (`Play`, `Pause`, `Next Day`, `Reset`).
  * Real-time portfolio equity curve synchronized with active trades and tinted trade log.
  * Apache HBase low-latency serving layer enabling sub-second historical trade queries.

---

### Slide 15: Team Contributions & Role Distribution

* **Slide Category:** Project Team Ownership Matrix
* **Lead Statement:**
  > Clear division of engineering ownership across data architecture, storage, analytics, machine learning, and quantitative backtesting.
* **Individual Ownership & Slide Coverage:**
  * **Aditya Medhane (`2023BCS-003`) — Slides 2, 3, 4:**
    * *Focus:* Project Overview & Pipeline, Big Data Tools & Tech Stack, NIFTY 100 Dataset Curation & 6.85M Volume Quantification.
  * **Vishwas Kulkarni (`2023BCS-072`) — Slides 5, 6, 7:**
    * *Focus:* 7-Container Docker Cluster & HDFS Architecture, Spark ETL & Pig Data Cleaning, Analytics & Multi-Source Signal Ingestion.
  * **Atharv Jagzap (`2023BCS-012`) — Slides 8, 9, 10, 11:**
    * *Focus:* Multi-Source Scoring Engine & Academic References, Spark MLlib Model Training & Hyperparameters, Technical Trading Indicators, Final Score & Decision Logic (Core Slide 11).
  * **Amogh Deshpande (`2023BCS-018`) — Slides 12, 13, 14:**
    * *Focus:* Backtest Simulator Methodology & Execution Setup, Realistic Performance Metrics (50–52% Accuracy & Expectancy), Day-by-Day Trade Replay & Dashboard Integration.

---
*End of StockPulse Presentation Context Document. Ready for Claude PPT Generation.*
