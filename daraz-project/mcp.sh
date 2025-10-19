#!/bin/bash
# MCP (Maintenance / Continuous Processing) automation script
# Runs daily or periodically to refresh scraped data and regenerate models

set -e
cd "$(dirname "$0")"

timestamp=$(date -u +"%Y%m%dT%H%M%SZ")

echo "[MCP] Starting pipeline at $timestamp"
python3 scraper.py
python3 preprocess.py
python3 dims.py
cp artifacts/dims.pkl artifacts/dims-$timestamp.pkl
echo "[MCP] Completed successfully at $timestamp"
