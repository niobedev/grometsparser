#!/bin/bash
set -e

# Configuration
REPO_OWNER="niobedev"
REPO_NAME="grometsparser"
WEB_ROOT="/var/www/gromets"
BACKUP_DIR="/var/backups/gromets"

echo "=== Gromet's Plaza Archive Deployment Script ==="
echo "Fetching latest release from GitHub..."

# Get the latest release archive URL
ARCHIVE_URL=$(curl -s https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest | grep -o '"browser_download_url": "[^"]*' | cut -d'"' -f4)

if [ -z "$ARCHIVE_URL" ]; then
    echo "Error: Could not fetch release URL"
    exit 1
fi

echo "Downloading: $ARCHIVE_URL"

# Backup existing deployment
if [ -d "$WEB_ROOT" ]; then
    echo "Creating backup..."
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/gromets-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    tar -czf "$BACKUP_FILE" -C "$WEB_ROOT" .
    echo "Backup created: $BACKUP_FILE"
fi

# Download new archive
wget -q --show-progress "$ARCHIVE_URL" -O /tmp/website-archive.tar.gz

# Extract to temporary directory
echo "Extracting archive..."
rm -rf /tmp/website-new
mkdir -p /tmp/website-new
tar -xzf /tmp/website-archive.tar.gz -C /tmp/website-new

# Deploy to web root
echo "Deploying to $WEB_ROOT..."
mkdir -p "$WEB_ROOT"
rsync -av --delete /tmp/website-new/public/ "$WEB_ROOT/"

# Cleanup
rm -rf /tmp/website-new /tmp/website-archive.tar.gz

echo "=== Deployment completed successfully ==="
echo "Website is now available at: $WEB_ROOT"
