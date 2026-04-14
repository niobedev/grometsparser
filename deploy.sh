#!/bin/bash
set -e

# Configuration
REPO_OWNER="niobedev"
REPO_NAME="grometsparser"
WEB_ROOT="/var/www/gromets"
BACKUP_DIR="/var/backups/gromets"

echo "=== Gromet's Plaza Archive Deployment Script ==="
echo "Fetching latest release from GitHub..."

# Get latest release archive URL
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

# Verify archive integrity
echo "Verifying archive..."
if ! tar -tzf /tmp/website-archive.tar.gz >/dev/null 2>&1; then
    echo "Error: Archive is corrupted or invalid"
    exit 1
fi

# Extract to temporary directory
echo "Extracting archive..."
rm -rf /tmp/website-new
mkdir -p /tmp/website-new
tar -xzf /tmp/website-archive.tar.gz -C /tmp/website-new

# Verify extraction
echo "Verifying extraction..."
if [ ! -d "/tmp/website-new/public" ]; then
    echo "Error: public/ directory not found in archive"
    echo "Archive contents:"
    tar -tzf /tmp/website-archive.tar.gz | head -20
    exit 1
fi

# Check for HTML files
HTML_COUNT=$(find /tmp/website-new/public -name "*.html" | wc -l)
echo "Found $HTML_COUNT HTML files in archive"
if [ "$HTML_COUNT" -eq 0 ]; then
    echo "Error: No HTML files found in archive!"
    echo "Archive structure:"
    find /tmp/website-new/public -type f | head -20
    exit 1
fi

# Show sample structure
echo "Sample directory structure:"
ls -la /tmp/website-new/public/
echo ""
ls -la /tmp/website-new/public/stories/ | head -10

# Deploy to web root
echo "Deploying to $WEB_ROOT..."
mkdir -p "$WEB_ROOT"
rsync -av --delete /tmp/website-new/public/ "$WEB_ROOT/"

# Verify deployment
echo "Verifying deployment..."
DEPLOYED_HTML_COUNT=$(find "$WEB_ROOT" -name "*.html" | wc -l)
echo "Deployed $DEPLOYED_HTML_COUNT HTML files to $WEB_ROOT"

if [ "$DEPLOYED_HTML_COUNT" -eq 0 ]; then
    echo "Error: No HTML files were deployed!"
    exit 1
fi

# Cleanup
rm -rf /tmp/website-new /tmp/website-archive.tar.gz

echo "=== Deployment completed successfully ==="
echo "Website is now available at: $WEB_ROOT"
echo "HTML files in deployment: $DEPLOYED_HTML_COUNT"
