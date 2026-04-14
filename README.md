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
- 🚀 **Automated Daily Sync:** Docker-based daily sync with automatic git commits and website rebuilding.

## 📂 Project Structure

- `stories/` - Raw HTML files from the original site (committed).
- `website/` - The Hugo-based web frontend.
- `extract_urls.py` - Script to extract all story URLs from the author index pages.
- `download_stories.py` - The main scraping engine with 404 tracking.
- `convert_to_markdown.py` - Bridge script to move raw data into the web directory.
- `detect_broken_markdown.py` - Quality control utility for fixing formatting.
- `sync.py` - Core sync script with git commit functionality.
- `daily_sync.sh` - Complete daily sync workflow for Docker automation.
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

The project is designed to be managed via `make` commands:

### Step 1: Extract URLs
Fetch all story URLs from the author index pages:
```bash
# Run this manually (not in Makefile)
python3 extract_urls.py
```

### Step 2: Downloading
Fetch new stories that aren't already in your `stories/` folder:
```bash
make download
```
*Failed URLs (404s) are tracked in `failed_urls.json` to avoid redundant requests.*

### Step 3: Quality Control
Before publishing, check if any stories have rendering issues:
```bash
# Detect broken formatting
python3 detect_broken_markdown.py

# Delete identified broken files (optional, allows re-parsing)
python3 detect_broken_markdown.py --delete
```

### Step 4: Conversion & Build
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

#### Daily Sync (Recommended)

This will check for new stories, download them, convert to markdown, commit changes to git, and rebuild the website:

```bash
# Run daily sync with git commits
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash daily_sync.sh
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

### Setting Up Daily Cron Job

To run the sync daily at 2 AM, add this to your crontab:

```bash
# Edit crontab
crontab -e

# Add entry to run Docker sync daily at 2 AM
0 2 * * * cd /path/to/your/repository && docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash daily_sync.sh >> /var/log/gromets-sync.log 2>&1
```

### Manual Docker Run Examples

```bash
# Run daily sync with git commits (recommended)
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash daily_sync.sh

# Run simple sync and build without git
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

# Run only sync without build
docker run --rm \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 sync.py
```

### Daily Sync Script Details

The `daily_sync.sh` script provides a complete automated workflow:

1. **HTTPS Setup**: Configures HTTPS authentication for git operations using GitHub token
2. **Git Configuration**: Sets up git user for commits
3. **Repository Sync**: Pulls latest changes if needed
4. **Story Sync**: Runs `sync.py` to check for new stories
5. **URL Extraction**: Updates story URL list
6. **Download**: Downloads any new stories
7. **Conversion**: Converts stories to markdown
8. **Git Commit**: Commits new stories with descriptive message
9. **Website Build**: Builds the Hugo site
10. **Logging**: Provides detailed logging throughout the process

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
