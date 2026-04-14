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
echo "[2/2] Building website to /var/www..."
cd website && hugo --destination ../public --quiet || hugo --destination ../public
cd ..

echo "Copying built site to /var/www..."
cp -r website/public/* /var/www/

echo ""
echo "=========================================="
echo "Build completed successfully"
echo "=========================================="