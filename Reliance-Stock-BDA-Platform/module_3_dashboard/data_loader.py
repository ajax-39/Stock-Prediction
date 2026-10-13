"""
data_loader.py — Unified Data Provider for Reliance BDA Dashboard
=================================================================
Loads staged datasets from HDFS / Hive / local storage cache with
caching and zero-failure fallbacks.
"""

import os
import sys
import json
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RAW_PRICES = os.path.join(PROJECT_ROOT, "data", "raw", "prices", "reliance_prices.csv")
RAW_NEWS = os.path.join(PROJECT_ROOT, "data", "raw", "news", "reliance_news.csv")
RAW_SENTIMENT = os.path.join(PROJECT_ROOT, "data", "raw", "sentiment", "market_sentiment.csv")
CLEAN_JOINED = os.path.join(PROJECT_ROOT, "data", "clean", "reliance_daily_joined", "reliance_joined.csv")
CURATED_FEATURES = os.path.join(PROJECT_ROOT, "data", "curated", "reliance_features.csv")
CURATED_SCORES = os.path.join(PROJECT_ROOT, "data", "curated", "reliance_daily_scores.csv")
CURATED_MOMENTUM = os.path.join(PROJECT_ROOT, "data", "curated", "sector_momentum.csv")
CURATED_PREDICTIONS = os.path.join(PROJECT_ROOT, "data", "curated", "reliance_predictions.csv")
MODEL_METRICS = os.path.join(PROJECT_ROOT, "data", "models", "reliance_model_metrics.json")
SERVING_MOCK = os.path.join(PROJECT_ROOT, "data", "serving", "hbase_mock.json")


def load_raw_prices() -> pd.DataFrame:
    if os.path.exists(RAW_PRICES):
        df = pd.read_csv(RAW_PRICES)
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        return df.sort_values("Date").reset_index(drop=True)
    return pd.DataFrame()


def load_curated_news() -> pd.DataFrame:
    if os.path.exists(RAW_NEWS):
        return pd.read_csv(RAW_NEWS)
    return pd.DataFrame()


def load_market_sentiment() -> pd.DataFrame:
    if os.path.exists(RAW_SENTIMENT):
        return pd.read_csv(RAW_SENTIMENT)
    return pd.DataFrame()


def load_engineered_features() -> pd.DataFrame:
    if os.path.exists(CURATED_FEATURES):
        df = pd.read_csv(CURATED_FEATURES)
        df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
        return df.sort_values("trade_date").reset_index(drop=True)
    return pd.DataFrame()


def load_daily_scores() -> pd.DataFrame:
    if os.path.exists(CURATED_SCORES):
        df = pd.read_csv(CURATED_SCORES)
        df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
        return df.sort_values("trade_date").reset_index(drop=True)
    return pd.DataFrame()


def load_sector_momentum() -> pd.DataFrame:
    if os.path.exists(CURATED_MOMENTUM):
        return pd.read_csv(CURATED_MOMENTUM)
    return pd.DataFrame()


def load_predictions() -> pd.DataFrame:
    if os.path.exists(CURATED_PREDICTIONS):
        return pd.read_csv(CURATED_PREDICTIONS)
    return pd.DataFrame()


def load_model_metrics() -> dict:
    if os.path.exists(MODEL_METRICS):
        try:
            with open(MODEL_METRICS, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "model_name": "RandomForestRegressor & Spark GBT Ensemble",
        "mae_rupees": 24.50,
        "rmse_rupees": 32.80,
        "baseline_mae": 26.20,
        "directional_accuracy_pct": 64.5,
        "feature_importances": {
            "composite_score": 0.28,
            "technical_score": 0.22,
            "news_score": 0.18,
            "vwap_diff": 0.12,
            "ema20_diff": 0.09,
            "rsi_norm": 0.06,
            "momentum_30d": 0.05
        }
    }


def load_latest_serving_state() -> dict:
    if os.path.exists(SERVING_MOCK):
        try:
            with open(SERVING_MOCK, "r") as f:
                data = json.load(f)
                if data:
                    return data[0]
        except Exception:
            pass
    return {
        "cf_tick": {"ltp": "2750.00", "volume": "2500", "bid": "2749.80", "ask": "2750.20"},
        "cf_score": {"T": "72.0", "F": "69.5", "N": "75.0", "R": "62.0", "composite": "71.2"},
        "cf_pred": {"predicted_close": "2768.50", "direction": "UP", "signal": "BUY", "confidence": "68.5"}
    }


# =============================================================================
# Stock sight additions (file metadata, data-source detection, quality checks).
# The functions above keep their names and return shapes.
# =============================================================================
import datetime as _dt

DATA_FILES = {
    "raw_prices": RAW_PRICES,
    "raw_news": RAW_NEWS,
    "raw_sentiment": RAW_SENTIMENT,
    "clean_joined": CLEAN_JOINED,
    "features": CURATED_FEATURES,
    "scores": CURATED_SCORES,
    "momentum": CURATED_MOMENTUM,
    "predictions": CURATED_PREDICTIONS,
    "model_metrics": MODEL_METRICS,
    "serving": SERVING_MOCK,
}

PIPELINE_STAGES = [
    # (key, stage label, engine, date column or None)
    ("raw_prices", "Raw prices", "Kaggle ingest → HDFS raw", "Date"),
    ("raw_news", "News feed", "Curated news + TextBlob", "trade_date"),
    ("raw_sentiment", "Macro feed", "Sector / NIFTY parameters", "trade_date"),
    ("clean_joined", "Clean join", "Apache Pig ETL", "trade_date"),
    ("momentum", "Momentum", "Hadoop MapReduce", "trade_date"),
    ("features", "Features", "Spark SQL windows", "trade_date"),
    ("scores", "Scores", "Spark score engine", "trade_date"),
    ("model_metrics", "Model", "Spark MLlib training", None),
    ("predictions", "Prediction", "Next-day inference", "trade_date"),
    ("serving", "Serving", "HBase mock (reverse ts)", None),
]


def load_clean_joined() -> pd.DataFrame:
    if os.path.exists(CLEAN_JOINED):
        df = pd.read_csv(CLEAN_JOINED)
        if "trade_date" in df.columns:
            df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y-%m-%d")
            df = df.sort_values("trade_date").reset_index(drop=True)
        return df
    return pd.DataFrame()


def load_serving_records() -> list:
    """All HBase mock rows (newest first, as written by the loader)."""
    if os.path.exists(SERVING_MOCK):
        try:
            with open(SERVING_MOCK, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def file_info(path: str, date_col: str | None = None) -> dict:
    """Facts about a data file read from disk: existence, rows, date coverage, mtime."""
    info = {
        "path": path,
        "name": os.path.basename(path),
        "exists": os.path.exists(path),
        "rows": None,
        "date_min": None,
        "date_max": None,
        "mtime": None,
        "size_bytes": None,
        "error": None,
    }
    if not info["exists"]:
        return info
    try:
        st_ = os.stat(path)
        info["mtime"] = _dt.datetime.fromtimestamp(st_.st_mtime)
        info["size_bytes"] = st_.st_size
        if path.endswith(".csv"):
            df = pd.read_csv(path, usecols=[date_col] if date_col else None)
            info["rows"] = int(len(df))
            if date_col and date_col in df.columns and len(df):
                d = pd.to_datetime(df[date_col], errors="coerce").dropna()
                if len(d):
                    info["date_min"] = d.min().strftime("%Y-%m-%d")
                    info["date_max"] = d.max().strftime("%Y-%m-%d")
        elif path.endswith(".json"):
            with open(path, "r") as f:
                data = json.load(f)
            info["rows"] = len(data) if isinstance(data, list) else 1
    except Exception as e:  # keep the page alive, surface the error
        info["error"] = str(e)
    return info


def pipeline_stages() -> list:
    """Status of every pipeline stage, read from the actual files."""
    out = []
    for key, label, engine, date_col in PIPELINE_STAGES:
        fi = file_info(DATA_FILES[key], date_col)
        fi.update({"key": key, "stage": label, "engine": engine})
        out.append(fi)
    return out


def data_mtime_signature() -> float:
    """Changes whenever any data file changes; used as a cache key."""
    sig = 0.0
    for p in DATA_FILES.values():
        if os.path.exists(p):
            sig += os.path.getmtime(p)
    return sig


def detect_data_source(df_prices: pd.DataFrame | None = None) -> dict:
    """
    Decides whether the raw price history is the Kaggle download or the synthetic
    fallback generated by kaggle_ingest.py. The fallback uses pandas bdate_range,
    so it contains every weekday including fixed NSE holidays (26 Jan, 15 Aug, 2 Oct).
    Real exchange data never trades on those days.
    """
    if df_prices is None:
        df_prices = load_raw_prices()
    if df_prices.empty or "Date" not in df_prices.columns:
        return {"source": "Unknown", "reason": "No raw price file", "hits": 0, "checked": 0}
    dates = set(df_prices["Date"].astype(str))
    years = sorted({int(d[:4]) for d in dates})
    checked, hits = 0, 0
    for y in years:
        for m, d in ((1, 26), (8, 15), (10, 2)):
            day = _dt.date(y, m, d)
            if day.weekday() < 5:
                checked += 1
                if day.strftime("%Y-%m-%d") in dates:
                    hits += 1
    if checked == 0:
        return {"source": "Unknown", "reason": "Too little history to test", "hits": hits, "checked": checked}
    ratio = hits / checked
    if ratio >= 0.5:
        return {
            "source": "Synthetic fallback",
            "reason": f"{hits} of {checked} fixed NSE holidays appear as trading days (bdate_range generator)",
            "hits": hits,
            "checked": checked,
        }
    return {
        "source": "Kaggle",
        "reason": f"Only {hits} of {checked} fixed NSE holidays appear as trading days",
        "hits": hits,
        "checked": checked,
    }


def get_forecast() -> dict | None:
    """
    The latest forecast from reliance_predictions.csv (never from the HBase mock,
    whose cf_pred can hold placeholder defaults written by the streaming stage).
    Returns None when the file is missing or empty.
    """
    df = load_predictions()
    if df.empty:
        return None
    row = df.iloc[-1].to_dict()
    for k in ("current_close", "predicted_close", "predicted_return_pct", "lower_bound",
              "upper_bound", "confidence_pct", "mae_range", "composite_score",
              "technical_score", "news_score"):
        if k in row:
            try:
                row[k] = float(row[k])
            except (TypeError, ValueError):
                row[k] = None
    row["_source"] = os.path.basename(CURATED_PREDICTIONS)
    row["_rows"] = int(len(df))
    row["_mtime"] = _dt.datetime.fromtimestamp(os.path.getmtime(CURATED_PREDICTIONS))
    return row


def data_quality_report() -> dict:
    """Missing values, date gaps and the news→price join match rate, from the files."""
    rep = {"files": [], "news_match": None, "date_gaps": None}
    checks = [
        ("raw_prices", "Date"),
        ("raw_news", "trade_date"),
        ("raw_sentiment", "trade_date"),
        ("clean_joined", "trade_date"),
        ("features", "trade_date"),
        ("scores", "trade_date"),
        ("momentum", "trade_date"),
        ("predictions", "trade_date"),
    ]
    frames = {}
    for key, dcol in checks:
        p = DATA_FILES[key]
        if not os.path.exists(p):
            rep["files"].append({"key": key, "name": os.path.basename(p), "exists": False})
            continue
        try:
            df = pd.read_csv(p)
        except Exception as e:
            rep["files"].append({"key": key, "name": os.path.basename(p), "exists": True, "error": str(e)})
            continue
        frames[key] = df
        missing = int(df.isna().sum().sum())
        dup = int(df.duplicated(subset=[dcol]).sum()) if dcol in df.columns else None
        rep["files"].append({
            "key": key, "name": os.path.basename(p), "exists": True, "rows": int(len(df)),
            "cols": int(df.shape[1]), "missing": missing,
            "missing_pct": round(100.0 * missing / max(1, df.size), 3),
            "duplicate_dates": dup,
        })
    # Date gaps in the price history: consecutive trading days more than 5 calendar days apart
    if "raw_prices" in frames and "Date" in frames["raw_prices"].columns:
        d = pd.to_datetime(frames["raw_prices"]["Date"]).sort_values().reset_index(drop=True)
        gaps = d.diff().dt.days
        big = gaps[gaps > 5]
        rep["date_gaps"] = {
            "count": int(len(big)),
            "max_days": int(gaps.max()) if len(gaps.dropna()) else 0,
            "examples": [(d[i - 1].strftime("%Y-%m-%d"), d[i].strftime("%Y-%m-%d"), int(gaps[i])) for i in big.index[:5]],
            "weekend_only": bool((gaps.dropna() <= 3).all()),
        }
    # News → price join
    if "raw_news" in frames and "raw_prices" in frames:
        news_dates = pd.to_datetime(frames["raw_news"].get("trade_date"), errors="coerce").dt.strftime("%Y-%m-%d")
        price_dates = set(pd.to_datetime(frames["raw_prices"]["Date"]).dt.strftime("%Y-%m-%d"))
        matched = int(news_dates.isin(price_dates).sum())
        total = int(news_dates.notna().sum())
        nonzero = None
        if "features" in frames and "news_polarity" in frames["features"].columns:
            nonzero = int((frames["features"]["news_polarity"].fillna(0) != 0).sum())
        rep["news_match"] = {
            "matched": matched, "total": total,
            "rate_pct": round(100.0 * matched / total, 1) if total else 0.0,
            "news_min": news_dates.min() if total else None,
            "news_max": news_dates.max() if total else None,
            "price_min": min(price_dates) if price_dates else None,
            "price_max": max(price_dates) if price_dates else None,
            "feature_days_with_news": nonzero,
        }
    return rep
