#!/bin/bash
# ============================================================================
# run_mapreduce.sh — Hadoop Streaming Job Execution for Sector Momentum
# ============================================================================
set -e

INPUT_PATH="/bda/lake/clean/reliance_daily_joined"
OUTPUT_PATH="/bda/lake/curated/sector_momentum"

echo "=== Launching Hadoop Streaming MapReduce Job ==="

# Remove prior output in HDFS if existing
hdfs dfs -rm -r -f ${OUTPUT_PATH} || true

hadoop jar ${HADOOP_HOME}/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -files module_2_processing/mapreduce/sector_momentum_mapper.py,module_2_processing/mapreduce/sector_momentum_reducer.py \
    -mapper "python3 sector_momentum_mapper.py" \
    -reducer "python3 sector_momentum_reducer.py" \
    -input ${INPUT_PATH} \
    -output ${OUTPUT_PATH}

echo "✅ MapReduce Job completed. Output located at HDFS: ${OUTPUT_PATH}"
