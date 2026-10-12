#!/bin/bash
# ============================================================================
# hdfs_lake_setup.sh — HDFS 3-Zone Data Lake Initialization
# ============================================================================
set -e

echo "=== Initializing HDFS 3-Zone Data Lake for Reliance Platform ==="

# 1. Raw Zone (Immutable raw ingestion files)
echo "  [1/3] Creating HDFS Raw Zone..."
hdfs dfs -mkdir -p /bda/lake/raw/prices
hdfs dfs -mkdir -p /bda/lake/raw/news
hdfs dfs -mkdir -p /bda/lake/raw/sentiment

# 2. Clean Zone (Deduplicated, joined, and normalized schema)
echo "  [2/3] Creating HDFS Clean Zone..."
hdfs dfs -mkdir -p /bda/lake/clean/reliance_daily_joined

# 3. Curated Zone (Engineered feature tables & trained models)
echo "  [3/3] Creating HDFS Curated & Models Zone..."
hdfs dfs -mkdir -p /bda/lake/curated
hdfs dfs -mkdir -p /bda/models/reliance_mllib_best

# Set full cluster read/write permissions
hdfs dfs -chmod -R 777 /bda

echo "✅ HDFS Data Lake directories initialized successfully:"
hdfs dfs -ls -R /bda/lake
