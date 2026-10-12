#!/bin/bash
# ============================================================================
# zookeeper_kafka_setup.sh — Initialize Kafka Topics for Speed Layer
# ============================================================================
set -e

BOOTSTRAP_SERVER="kafka:9092"
echo "=== Setting up Kafka Topics on ${BOOTSTRAP_SERVER} ==="

# 1. Topic for live broker ticks
echo "  [1/2] Creating topic: reliance-ticks..."
kafka-topics --bootstrap-server ${BOOTSTRAP_SERVER} \
             --create --if-not-exists \
             --topic reliance-ticks \
             --partitions 3 \
             --replication-factor 1

# 2. Topic for incoming breaking financial news
echo "  [2/2] Creating topic: reliance-news..."
kafka-topics --bootstrap-server ${BOOTSTRAP_SERVER} \
             --create --if-not-exists \
             --topic reliance-news \
             --partitions 1 \
             --replication-factor 1

echo "✅ Active Kafka Topics:"
kafka-topics --bootstrap-server ${BOOTSTRAP_SERVER} --list
