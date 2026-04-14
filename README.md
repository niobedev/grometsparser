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
- 🚀 **One-Click Deployment:** Build the site and create a deployable archive with a single command.

## 📂 Project Structure

- `stories/` - Raw HTML files from the original site (committed).
- `website/` - The Hugo-based web frontend.
- `extract_urls.py` - Script to extract all story URLs from the author index pages.
- `download_stories.py` - The main scraping engine with 404 tracking.
- `convert_to_markdown.py` - Bridge script to move raw data into the web directory.
- `detect_broken_markdown.py` - Quality control utility for fixing formatting.
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

## 🚢 Deployment

### Manual Build
Run `make build` and upload the contents of the generated `website-archive.tar.gz` to your web server's root.

### Docker Deployment

The project includes a Docker container for automated daily sync and deployment.

#### Prerequisites

- **Docker**
- **GitHub CLI** (`gh`) or Docker Hub access token (for private images)
- **SSH key** with push access to the repository (for automated commits)

#### Building the Image

```bash
# Build the image locally
docker build -t grometsparser:latest .

# Or pull from GitHub Container Registry after pushing a tag
docker pull ghcr.io/niobedev/grometsparser:latest
```

#### Running the Container

```bash
# Run sync and build, committing new stories to GitHub
docker run --rm \
  -v /path/to/your/ssh-key:/home/appuser/.ssh/id_ed25519:ro \
  -v /path/to/output:/var/www \
  -e GIT_AUTHOR_NAME="Your Name" \
  -e GIT_AUTHOR_EMAIL="your@email.com" \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash sync_and_build.sh
```

Required volume mounts:
- `/path/to/your/ssh-key` - Your SSH private key with GitHub push access (read-only)
- `/path/to/output` - Directory where the built site will be written (mounted to `/var/www`)

Optional environment variables:
- `GIT_AUTHOR_NAME` - Name for git commits (default: "Gromet's Parser")
- `GIT_AUTHOR_EMAIL` - Email for git commits (default: "parser@gromets.local")

#### Running with Cron

To run daily at a specific time, use a cron job on the host machine:

```bash
# Edit crontab
crontab -e

# Add entry to run Docker sync daily at 2 AM
0 2 * * * docker run --rm \
  -v /home/user/.ssh/id_ed25519:/home/appuser/.ssh/id_ed25519:ro \
  -v /var/www:/var/www \
  -e GIT_AUTHOR_NAME="Your Name" \
  -e GIT_AUTHOR_EMAIL="your@email.com" \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash sync_and_build.sh >> /var/log/gromets-sync.log 2>&1
```

#### Triggering Docker Build

The Docker image is automatically built and pushed to GitHub Container Registry when you push a tag:

```bash
# Tag and push a new version
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

The image will be available at:
- `ghcr.io/niobedev/grometsparser:v1.0.0`
- `ghcr.io/niobedev/grometsparser:latest` (for latest tag)

#### Manual Docker Run Examples

```bash
# Run sync only (check for new stories, commit if any)
docker run --rm \
  -v ~/.ssh/id_ed25519:/home/appuser/.ssh/id_ed25519:ro \
  ghcr.io/niobedev/grometsparser:latest \
  python3 sync.py

# Run full sync and build
docker run --rm \
  -v ~/.ssh/id_ed25519:/home/appuser/.ssh/id_ed25519:ro \
  -v /var/www:/var/www \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash sync_and_build.sh

# Run with retry of previously failed URLs
docker run --rm \
  -v ~/.ssh/id_ed25519:/home/appuser/.ssh/id_ed25519:ro \
  ghcr.io/niobedev/grometsparser:latest \
  python3 download_stories.py --retry-failed
```

## ⚖️ License & Copyright

**Stories are copyrighted by their respective authors.** Duplication of any kind is prohibited without express consent from the original creators. This software is provided for archival and educational purposes.

All credits and original rights belong to the authors and Gromet's Plaza. The stories remain the copyright property of their respective authors.
