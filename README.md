# 🏛️ Gromet's Plaza Archive Parser

> A high-performance parser and modern web archive for preserving stories from Gromet's Plaza.

## 📜 Purpose

This repository contains the tools to scrape, clean, and re-host stories from [Gromet's Plaza](https://grometsplaza.net/), a comprehensive collection of adult stories featuring bondage, fetish, latex, and various other themes.

> 🔞 **Adult Content Warning:** This site contains adult/explicit content intended for mature audiences only.

## ✨ Features

- ⚡ **High-Speed Parsing:** Efficient Python-based scraper with failure tracking and polite request delays.
- 🔍 **Fast Search:** Integrated search functionality with debounced input and minimum character requirements for performance.
- 📱 **Responsive Design:** Based on the clean and minimalist `PaperMod` Hugo theme.
- 🎨 **Smart Markdown Correction:** Automatic detection and fixing of common formatting issues (broken italics, malformed author's notes).
- 🏷️ **Rich Metadata:** Stories include author tags, story codes, and links to the original source.
- 🚀 **Automated Two-Tier Sync:** Docker-based hourly quick sync and weekly full sync with automatic git commits and website rebuilding.

## 📂 Project Structure

- `stories/` - Raw HTML files from the original site (committed).
- `website/` - The Hugo-based web frontend.
- `extract_urls.py` - Script to extract all story URLs from the author index pages.
- `download_stories.py` - The main scraping engine with 404 tracking.
- `convert_to_markdown.py` - Bridge script to move raw data into the web directory.
- `detect_broken_markdown.py` - Quality control utility for fixing formatting.
- `sync.py` - Core full sync script with git commit functionality.
- `quick_sync.py` - Quick sync script that checks only the "Updates" section for hourly runs.
- `sync_and_build.sh` - Simple sync and build without git operations.
- `Makefile` - The automation hub for all common tasks.

## 🛠️ Quick Start

### 1. Prerequisites
- **Python 3.x** & `pip`
- **[Hugo Extended](https://gohugo.io/installation/)** (v0.120+ recommended)
- **Make** (optional, but highly recommended)

### 2. Installation
```bash
# Clone the repository and its theme submodule
git clone <repository-url> grometsparser
cd grometsparser
git submodule update --init --recursive

# Set up the Python virtual environment
make venv
```

## ⚙️ Usage Workflow

The project is designed to be managed via `make` commands and supports a two-tier sync approach:

### Two-Tier Sync Strategy

**Quick Sync (Hourly)**
- **Purpose**: Fast, lightweight check for recently posted stories
- **Source**: Checks only the "Updates" section on https://grometsplaza.net/main.html
- **Performance**: Very fast, only checks 20-30 recent stories
- **Usage**: `make quick-sync` or `make docker-run-quick`

**Full Sync (Weekly)**
- **Purpose**: Complete scan of all story sites
- **Source**: Scans all 19 story sites using search pagination
- **Performance**: Heavy process, downloads and processes thousands of stories
- **Usage**: `make sync` or `make docker-run`

### Manual Workflow

#### Step 1: Extract URLs
Fetch all story URLs from the author index pages:
```bash
# Run this manually (not in Makefile)
python3 extract_urls.py
```

#### Step 2: Downloading
Fetch new stories that aren't already in your `stories/` folder:
```bash
make download
```
*Failed URLs (404s) are tracked in `failed_urls.json` to avoid redundant requests.*

#### Step 3: Quality Control
Before publishing, check if any stories have rendering issues:
```bash
# Detect broken formatting
python3 detect_broken_markdown.py

# Delete identified broken files (optional, allows re-parsing)
python3 detect_broken_markdown.py --delete
```

#### Step 4: Conversion & Build
Prepare the data for Hugo and generate the static site:
```bash
# Sync stories to the website directory
make convert

# Build the site and create a website-archive.tar.gz archive
make build
```

### Step 5: Local Preview
```bash
cd website
hugo server
```

## 🚢 Docker Deployment

The project includes a Docker container for automated daily sync and deployment.

### Prerequisites

- **Docker**
- **GitHub CLI** (`gh`) or GitHub personal access token (for private images)
- **GitHub personal access token** with push access to the repository (for automated commits)

### Building the Image

The Docker image is automatically built and pushed to GitHub Container Registry when you push a tag:

```bash
# Tag and push a new version
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

The image will be available at:
- `ghcr.io/niobedev/grometsparser:v1.0.0`
- `ghcr.io/niobedev/grometsparser:latest` (for latest tag)

### Running the Container

The project directory is mounted into the container at `/app`. Your GitHub token should be provided as an environment variable to allow git commits:

#### Quick Sync (Hourly - Recommended)

This will check only the "Updates" section for recent stories, download any new ones, convert to markdown, and commit changes to git:

```bash
# Run quick sync with git commits
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 quick_sync.py
```

#### Full Sync (Weekly)

This will perform a complete scan of all story sites, download all new stories, convert to markdown, and commit changes to git:

```bash
# Run full sync with git commits
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 sync.py
```



#### Simple Sync and Build (No Git)

This will sync and build without making git commits:

```bash
# Run sync and build without git operations
docker run --rm \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash sync_and_build.sh
```

### Required Volume Mounts

For daily sync with git operations:
- `$(pwd)` - Current directory (your project repository) mounted to `/app`
- `GITHUB_TOKEN` - Environment variable with your GitHub personal access token with push permissions

The container mounts the project at `/app`, so output files (built site, committed stories) are written directly to the mounted host directory.

### Setting Up Automated Cron Jobs

For the two-tier sync approach, set up both hourly quick sync and weekly full sync:

```bash
# Edit crontab
crontab -e

# Quick sync - runs every hour at minute 5
5 * * * * cd /path/to/your/repository && docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 quick_sync.py >> /var/log/gromets-quick-sync.log 2>&1

# Full sync - runs every Sunday at 2 AM
0 2 * * 0 cd /path/to/your/repository && docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 sync.py >> /var/log/gromets-full-sync.log 2>&1
```

### Manual Docker Run Examples

```bash
# Quick sync with git commits (hourly recommended)
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 quick_sync.py

# Full sync with git commits (weekly recommended)
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 sync.py



# Simple sync and build without git
docker run --rm \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash sync_and_build.sh

# Run with retry of previously failed URLs
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 download_stories.py --retry-failed
```

### Sync Script Details

#### Quick Sync Script (`quick_sync.py`)
The `quick_sync.py` script provides an efficient hourly workflow:

1. **Fetch Main Page**: Retrieves https://grometsplaza.net/main.html
2. **Parse Updates Section**: Extracts recent stories from the "Updates" section
3. **Check Existing Stories**: Uses MD5 hashing to identify new stories
4. **Download New Stories**: Only downloads stories not already in database
5. **Convert to Markdown**: Converts new stories to website format
6. **Git Commit**: Commits new stories with descriptive message
7. **Cleanup**: Restores original story_urls.json

#### Full Sync Script (`sync.py`)
The `sync.py` script provides a complete weekly workflow:

1. **URL Extraction**: Updates story URL list from all 19 story sites
2. **Download All Stories**: Downloads all new stories across all sites
3. **Convert to Markdown**: Converts stories to website format
4. **Git Commit**: Commits new stories with descriptive message



### GitHub Actions

The repository includes a GitHub workflow that automatically builds and pushes Docker images to GitHub Container Registry when tags are pushed:

```yaml
name: Build and Push Docker Image

on:
  push:
    tags:
      - 'v*'
```

## 🚀 Deployment Options

### Manual Build
Run `make build` and upload the contents of the generated `website-archive.tar.gz` to your web server's root.

### Docker with Cron
Set up a cron job to run the Docker container daily. This is the recommended approach for automated updates.

### Serving the Website

After the Docker container runs, the built website is available in `website/public/`. You can serve this with any web server:

```bash
# Using nginx
sudo ln -s $(pwd)/website/public /var/www/gromets
sudo systemctl restart nginx

# Or using python's simple server
cd website/public
python3 -m http.server 8000
```

## ⚖️ License & Copyright

**Stories are copyrighted by their respective authors.** Duplication of any kind is prohibited without express consent from the original creators. This software is provided for archival and educational purposes.

All credits and original rights belong to the authors and Gromet's Plaza. The stories remain the copyright property of their respective authors.
