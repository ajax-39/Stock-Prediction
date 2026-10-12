#!/bin/bash
# ============================================================================
# Reliance Stock BDA Platform - Entrypoint Script
# Supports: master, datanode, dashboard
# ============================================================================
set -e

ROLE=${NODE_ROLE:-master}
echo "=========================================================="
echo " Starting Reliance BDA Node with Role: ${ROLE}"
echo " Hostname: $(hostname)"
echo "=========================================================="

service ssh start

if [ "${ROLE}" = "master" ]; then
    echo "[HADOOP MASTER] Initializing NameNode formatting..."
    if [ ! -d "/hadoop/dfs/name/current" ]; then
        hdfs namenode -format -force -nonInteractive
    fi

    echo "[HADOOP MASTER] Starting NameNode daemon..."
    hdfs --daemon start namenode

    echo "[HADOOP MASTER] Leaving safe mode if active..."
    hdfs dfsadmin -safemode wait || hdfs dfsadmin -safemode leave || true
    sleep 3
    hdfs dfsadmin -safemode leave || true

    echo "[HADOOP MASTER] Initializing HDFS Data Lake structure..."
    hdfs dfs -mkdir -p /spark-logs
    hdfs dfs -mkdir -p /bda/lake/raw/prices
    hdfs dfs -mkdir -p /bda/lake/raw/news
    hdfs dfs -mkdir -p /bda/lake/raw/sentiment
    hdfs dfs -mkdir -p /bda/lake/clean/reliance_daily_joined
    hdfs dfs -mkdir -p /bda/lake/curated
    hdfs dfs -mkdir -p /bda/models
    hdfs dfs -chmod -R 777 /bda /spark-logs

    echo "[HADOOP MASTER] Starting YARN ResourceManager..."
    yarn --daemon start resourcemanager

    echo "[SPARK MASTER] Starting Spark Master daemon..."
    ${SPARK_HOME}/sbin/start-master.sh

    echo "[MAPREDUCE] Starting HistoryServer..."
    mapred --daemon start historyserver

    echo "[STATUS] Hadoop Master and Spark services are healthy."

elif [ "${ROLE}" = "datanode" ]; then
    echo "[HADOOP DATANODE] Waiting for NameNode to be reachable..."
    until hdfs dfs -ls / > /dev/null 2>&1; do
        echo "Waiting for hadoop-master:9000..."
        sleep 2
    done

    echo "[HADOOP DATANODE] Starting DataNode daemon..."
    hdfs --daemon start datanode

    echo "[YARN] Starting NodeManager daemon..."
    yarn --daemon start nodemanager

    echo "[SPARK WORKER] Starting Spark Worker connecting to hadoop-master:7077..."
    ${SPARK_HOME}/sbin/start-worker.sh spark://hadoop-master:7077

    echo "[STATUS] DataNode and Worker services ready."

elif [ "${ROLE}" = "dashboard" ]; then
    echo "[DASHBOARD] Waiting for pipeline dependencies..."
    sleep 5
fi

# Keep container running
tail -f ${HADOOP_HOME}/logs/*.log 2>/dev/null || tail -f /dev/null
