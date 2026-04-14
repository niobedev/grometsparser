#!/bin/bash
set -e

echo "=========================================="
echo "Gromet's Plaza Sync and Build Script"
echo "=========================================="
echo "Started at: $(date '+%Y-%m-%d %H:%M:%S')"

echo ""
echo "[1/2] Running sync..."
python3 sync.py

echo ""
echo "[2/2] Building website..."
cd website && hugo

echo ""
echo "=========================================="
echo "Build completed successfully"
echo "Built site available in website/public"
echo "=========================================="