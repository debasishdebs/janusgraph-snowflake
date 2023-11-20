#!/usr/bin/env bash
conda activate snowflake-graphdb
databricker-connect test
conda deactivate

# bash memory-monitor.sh memory-monitor.logs 30162
# bash load-monitor.sh load-monitor.logs
