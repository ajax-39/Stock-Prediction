#!/bin/bash
# ============================================================================
# hbase_setup.sh — HBase Schema Definition for Low-Latency Serving
# ============================================================================
set -e

echo "=== Initializing HBase Tables for Reliance Stock Engine ==="

# HBase shell commands
hbase shell <<EOF
-- Disable and drop if recreating
disable 'reliance_serving'
drop 'reliance_serving'

-- Create table with 3 column families optimized for fast serving
create 'reliance_serving',
    {NAME => 'cf_tick', VERSIONS => 1, COMPRESSION => 'NONE', TTL => 604800},
    {NAME => 'cf_score', VERSIONS => 1, COMPRESSION => 'NONE'},
    {NAME => 'cf_pred', VERSIONS => 1, COMPRESSION => 'NONE'}

-- Describe table
describe 'reliance_serving'
exit
EOF

echo "✅ HBase table 'reliance_serving' created successfully."
