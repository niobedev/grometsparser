#!/bin/bash
set -e

echo "Running sync in Docker..."

# Configure git for automated commits
git config user.name 'Victoria Shayner'
git config user.email 'victoria.shayner@gmail.com'

# Set up git remote with token for pushing
git remote set-url origin https://${GITHUB_TOKEN}@github.com/niobedev/grometsparser.git

# Fetch latest changes
git fetch
git pull

# Run full sync script
python3 sync.py

# Restore git remote URL (remove token)
git remote set-url origin https://github.com/niobedev/grometsparser.git
