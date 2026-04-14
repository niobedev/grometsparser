#!/bin/bash
set -e

echo "Running quick sync in Docker..."

# Configure git for automated commits
git config user.name 'Victoria Shayner'
git config user.email 'victoria.shayner@gmail.com'

# Set up git remote with token for pushing
git remote set-url origin https://${GITHUB_TOKEN}@github.com/niobedev/grometsparser.git

# Fetch latest changes
git fetch
git pull

# Run quick sync script
python3 quick_sync.py
EXIT_CODE=$?

# Check if new stories were added and rebuild website if needed
if [ $EXIT_CODE -eq 1 ]; then
    echo 'New stories added.'
    # cd /app/website
    hugo --minify
    echo 'Website rebuilt successfully'
elif [ $EXIT_CODE -eq 0 ]; then
    echo 'No new stories, skipping website rebuild'
else
    echo 'Error in quick sync (exit code: $EXIT_CODE)'
    exit $EXIT_CODE
fi

# Restore git remote URL (remove token)
git remote set-url origin https://github.com/niobedev/grometsparser.git
