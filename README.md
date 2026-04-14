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
- 🚀 **Automated Hourly Sync:** Docker-based hourly quick sync with automatic git commits and conditional website rebuilding. Full sync available on-demand.
- 🔄 **CI/CD Pipeline:** Automatic website building and publishing to GitHub Releases on every push to main branch.

## 📂 Project Structure

- `stories/` - Raw HTML files from the original site (committed).
- `website/` - The Hugo-based web frontend.
- `download_stories.py` - The main scraping engine with 404 tracking.
- `convert_to_markdown.py` - Bridge script to move raw data into the web directory.
- `detect_broken_markdown.py` - Quality control utility for fixing formatting.
- `sync.py` - Core full sync script with git commit functionality.
- `quick_sync.py` - Quick sync script that checks only the "Updates" section for hourly runs.
- `docker-run.sh` - Shell script for Docker-based full sync.
- `docker-run-quick.sh` - Shell script for Docker-based quick sync with conditional website rebuild.
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

### 3. Environment Variables

Create a `.env` file in the project root (you can copy `.env.example` as a template):

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your GitHub token and Docker architecture
# Get your token from: https://github.com/settings/tokens
# The token needs push access to this repository
# DOCKER_ARCH: amd64 (most servers) or arm64 (Apple Silicon)
```

The `.env` file is automatically loaded by the Makefile. For Docker commands, you can either:
- Use the `.env` file (recommended - supports both `GITHUB_TOKEN` and `DOCKER_ARCH`)
- Pass environment variables directly (recommended for CI/CD)

## ⚙️ Usage Workflow

The project is designed to be managed via `make` commands and supports a two-tier sync approach:

### Two-Tier Sync Strategy

**Quick Sync (Hourly - Automated)**
- **Purpose**: Fast, lightweight check for recently posted stories
- **Source**: Checks only the "Updates" section on https://grometsplaza.net/main.html
- **Performance**: Very fast, only checks 20-30 recent stories
- **Usage**: `make docker-run-quick` (runs automatically via cron)

**Full Sync (Manual)**
- **Purpose**: Complete scan of all story sites
- **Source**: Scans all 19 story sites using search pagination
- **Performance**: Heavy process, downloads and processes thousands of stories
- **Usage**: `make sync` or `make docker-run` (run manually on demand only)

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
make serve
```

## 🚢 Docker Deployment

The project includes a Docker container for automated hourly sync (quick sync) and on-demand full sync.

### Prerequisites

- **Docker**
- **GitHub CLI** (`gh`) or GitHub personal access token (for private images)
- **GitHub personal access token** with push access to the repository (for automated commits)
- The Docker container comes pre-configured with git user settings for automated commits

### Building the Image

**Option 1: Set architecture in .env (Recommended)**
```bash
# Add to your .env file:
DOCKER_ARCH=amd64  # or arm64

# Then simply run:
make docker-build
```

**Option 2: Pass architecture as make argument**
```bash
# For x86_64 (most VPS servers)
make docker-build DOCKER_ARCH=amd64

# For ARM64 (Apple Silicon Macs)
make docker-build DOCKER_ARCH=arm64
```

The Docker image supports both architectures via the `HUGO_ARCH` build argument. The default is `amd64` for most servers.

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

The project directory is mounted into the container at `/app`. Your GitHub token should be provided as an environment variable to allow git commits.

**Option 1: Using .env file (Recommended for local development)**

```bash
# Create .env file with your GitHub token
echo "GITHUB_TOKEN=your_github_token_here" > .env

# Use make commands (they automatically load .env)
make docker-run-quick    # Quick sync (hourly)
make docker-run          # Full sync (weekly)
```

**Option 2: Passing GITHUB_TOKEN directly**

```bash
# Quick sync (hourly - automated)
make docker-run-quick

# Full sync (manual on-demand)
make docker-run
```



### Required Volume Mounts

For hourly automated quick sync with git operations:
- `$(pwd)` - Current directory (your project repository) mounted to `/app`
- `GITHUB_TOKEN` - Environment variable with your GitHub personal access token with push permissions

The container mounts the project at `/app`, so output files (built site, committed stories) are written directly to the mounted host directory.

### Setting Up Automated Cron Jobs

Quick sync runs automatically every hour to check for new stories in the "Updates" section:

```bash
# Edit crontab
crontab -e

# Quick sync - runs every hour at minute 5
5 * * * * cd /path/to/your/repository && make docker-run-quick >> /var/log/gromets-quick-sync.log 2>&1
```

**Note:** Full sync should be run manually on-demand when needed using `make docker-run` or `make sync`.

### Manual Docker Run Examples

For local development, you can use the `.env` file or pass `GITHUB_TOKEN` directly:

```bash
# Using .env file (recommended)
docker run --rm \
  --env-file .env \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 quick_sync.py

# Passing GITHUB_TOKEN directly
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 quick_sync.py
```

For full sync:

```bash
# Using .env file (recommended)
docker run --rm \
  --env-file .env \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 sync.py

# Passing GITHUB_TOKEN directly
docker run --rm \
  -e GITHUB_TOKEN=your_github_token \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  python3 sync.py
```

Other operations:

```bash
# Simple sync and build without git
docker run --rm \
  -v $(pwd):/app \
  ghcr.io/niobedev/grometsparser:latest \
  /bin/bash sync_and_build.sh

# Run with retry of previously failed URLs
docker run --rm \
  --env-file .env \
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
5. **Update URL List**: Adds new story URLs to `story_urls.json` (preserving existing URLs)
6. **Convert to Markdown**: Converts new stories to website format
7. **Git Commit**: Commits new stories and updated `story_urls.json` with descriptive message

#### Full Sync Script (`sync.py`)
The `sync.py` script provides a complete on-demand workflow for scanning all story sites:

1. **URL Extraction**: Updates story URL list from all 19 story sites
2. **Download All Stories**: Downloads all new stories across all sites
3. **Convert to Markdown**: Converts stories to website format
4. **Git Commit**: Commits new stories with descriptive message



### Docker Image Deployment

Docker images must be built and pushed manually to GitHub Container Registry:

```bash
# Build and tag Docker image
docker build -t ghcr.io/niobedev/grometsparser:latest .
docker tag ghcr.io/niobedev/grometsparser:latest ghcr.io/niobedev/grometsparser:v1.0.0

# Push to GitHub Container Registry
docker push ghcr.io/niobedev/grometsparser:latest
docker push ghcr.io/niobedev/grometsparser:v1.0.0
```

## 🚀 Deployment Options

### Automated Deployment (Recommended)

**Option 1: Use Deployment Script**

Copy `deploy.sh` to your VPS and run:

```bash
# Copy script to VPS
scp deploy.sh user@your-vps:/var/www/

# SSH to VPS and run
ssh user@your-vps
sudo ./deploy.sh
```

The script will:
- Download the latest release from GitHub
- Create a backup of the current deployment
- Extract and deploy the new version
- Clean up temporary files

**Option 2: Manual Download**

Download the latest website build from GitHub Releases after every push to `main`:

```bash
# Get the latest release archive URL
ARCHIVE_URL=$(curl -s https://api.github.com/repos/niobedev/grometsparser/releases/latest | grep -o '"browser_download_url": "[^"]*' | cut -d'"' -f4)

# Download archive
wget $ARCHIVE_URL -O website-archive.tar.gz

# Extract and deploy (creates public/ directory)
tar -xzf website-archive.tar.gz
cp -r public/* /var/www/gromets/
```

### Manual Build

Run `make build` and upload the contents of the generated `website/public/` directory to your web server's root.

### Docker with Cron
Set up a cron job to run the Docker container hourly for quick sync. This is the recommended approach for automated content updates.

### Serving the Website

The website files are available in `website/public/` (after manual build) or extracted from the release archive. You can serve them with any web server:

```bash
# Using nginx
sudo ln -s $(pwd)/website/public /var/www/gromets
sudo systemctl restart nginx

# Or using python's simple server
cd website/public
python3 -m http.server 8000
```

## 🔧 Troubleshooting

### "Exec format error" when running Docker container

If you encounter this error:
```
/usr/local/bin/hugo: cannot execute binary file: Exec format error
```

This indicates an architecture mismatch between your build environment and VPS. Rebuild the Docker image with the correct architecture:

**Option 1: Set in .env (Recommended)**
```bash
# Edit .env and set:
DOCKER_ARCH=amd64  # For x86_64 servers
# DOCKER_ARCH=arm64  # For ARM64 servers

# Rebuild
make docker-build
```

**Option 2: Pass as make argument**
```bash
# For x86_64 servers (most VPS including Hetzner, DigitalOcean, etc.)
make docker-build DOCKER_ARCH=amd64

# For ARM64 servers (Apple Silicon, some cloud instances)
make docker-build DOCKER_ARCH=arm64
```

## 🔄 GitHub Actions CI/CD

The repository includes an automated workflow that builds and publishes the website on every push to the `main` branch.

### Setup

The workflow is located at `.github/workflows/build-and-publish.yml` and requires:

1. **Enable GitHub Actions** - Go to repository Settings > Actions > General and verify "Allow all actions and reusable workflows" is enabled
2. **Permissions** - The workflow requires `contents: write` permission to create releases (already configured in the workflow file)
3. **GitHub Token** - Uses the built-in `secrets.GITHUB_TOKEN`, no additional setup required

### Workflow Details

- **Trigger**: Runs automatically on every push to `main` branch
- **Build Process**:
  1. Checks out the latest code
  2. Sets up Hugo Extended v0.146.6
  3. Builds the website with minification
  4. Creates a tar.gz archive of the `public/` directory
- **Release**: Creates a GitHub Release with:
  - Tag name: `build-YYYYMMDD-HHMMSS`
  - Release asset: `website-archive.tar.gz`
  - Release notes: Commit SHA, author, and message

### Using Automated Builds

Download the latest website build from GitHub Releases:

```bash
# Get the latest release URL
LATEST_URL=$(curl -s https://api.github.com/repos/niobedev/grometsparser/releases/latest | grep "browser_download_url" | cut -d '"' -f 4)

# Download and deploy
wget $LATEST_URL -O website-archive.tar.gz
tar -xzf website-archive.tar.gz
cp -r public/* /var/www/gromets/
```

Or manually download from:
https://github.com/niobedev/grometsparser/releases

### Manual Override

If you prefer to build locally instead of using automated releases, you can still use:

```bash
make build
```

## 🚨 Deployment Issues

### CI Build Error: Template Parse Failed (RESOLVED)

**Problem (Now Fixed):**
GitHub Actions workflow was showing:
```
Error: error building site: "/home/runner/work/grometsparser/.../taxonomy.html:44:1": parse of template failed: template: _default/taxonomy.html:44: unexpected EOF
Error: Process completed with exit code 1
```

**Root Cause:**
The Hugo theme (`PaperMod`) is a Git submodule. GitHub Actions doesn't clone submodules by default, so the custom layouts in `website/layouts/_default/` couldn't find theme partials like `anchored_headings.html`, causing template parsing to fail.

**Solution Implemented:**
Added `submodules: recursive` to GitHub Actions workflow checkout step:

```yaml
- name: Checkout code
  uses: actions/checkout@v4
  with:
    submodules: recursive  # This clones theme submodule
```

This ensures:
1. Hugo theme submodule is properly cloned
2. All theme partials are available to custom layouts
3. Template parsing succeeds without errors
4. Website builds correctly with all HTML files

### CI Build Warnings About Missing Layouts (RESOLVED)

**Problem (Now Fixed):**
GitHub Actions workflow was showing warnings about missing layout files:
```
WARN found no layout file for "html" for kind "taxonomy"
WARN found no layout file for "html" for kind "term"
WARN found no layout file for "html" for kind "section"
WARN found no layout file for "json" for kind "home"
```

**Why it happened:**
Hugo expects specific layout files for different page kinds (home, taxonomy, term, section). The PaperMod theme uses a flexible `list.html` approach that handles all these cases, but Hugo still searches for the specific files by default.

**Solution Implemented:**
Created custom layouts in `website/layouts/_default/` to provide Hugo with the files it expects:

1. **`index.html`** - Home page layout (based on theme's list.html)
2. **`taxonomy.html`** - Taxonomy listing pages (tags, authors)
3. **`term.html`** - Individual term pages (single tag/author)
4. **`section.html`** - Section pages (stories listing)
5. **`index.json`** - Search index generation for Fuse.js search

All these layouts follow the same structure and partials as the theme, ensuring consistent behavior.

**Result:**
CI workflow now completes without layout warnings and generates a proper release archive with all HTML files in the correct Hugo structure.

### No HTML files in extracted archive

**Problem:** GitHub Actions workflow shows warnings like:
```
WARN found no layout file for "html" for kind "home"
WARN found no layout file for "html" for kind "taxonomy"
WARN found no layout file for "html" for kind "term"
WARN found no layout file for "html" for kind "section"
```

**Why it happens:**
Hugo looks for specific layout files for different page kinds (home.html, taxonomy.html, etc.). The PaperMod theme uses a flexible `list.html` approach, but Hugo still searches for the specific files.

**Solution:**
The project includes a custom `website/layouts/_default/index.html` that's based on the theme's `list.html`. This provides Hugo with the layout file it expects and eliminates the warnings while maintaining theme functionality.

**Verification:**
The build completes successfully and generates proper HTML files in the expected Hugo structure (stories/YYYY/MM/DD/slug/index.html).

### No HTML files in extracted archive

If you extract the archive and find no `index.html` files or the website doesn't work:

```bash
# Check what's actually in the archive
tar -tzf website-archive.tar.gz | head -20

# Count HTML files in extraction
find /tmp/website-new/public -name "*.html" | wc -l

# List all files
find /tmp/website-new/public -type f | head -20
```

**Expected structure:**
```
public/
├── stories/2026/04/12/story-name/index.html  ← This is the story HTML
├── authors/author-name/index.html
├── tags/tag-name/index.html
├── index.html (homepage)
└── ...
```

If you see **no `index.html` files**, the Hugo build failed. Check:
1. GitHub Actions workflow logs for build errors
2. The "Verify build output" step should show HTML file count > 0
3. Look for Hugo configuration errors in the workflow run

### Deployment Script Verification

The `deploy.sh` script includes automatic verification:
- Checks archive integrity before extraction
- Verifies `public/` directory exists in archive
- Counts HTML files before and after deployment
- Shows detailed directory structure
- Fails with clear error messages if something is wrong

Check the script output for any "Error:" messages.

## ⚖️ License & Copyright

**Stories are copyrighted by their respective authors.** Duplication of any kind is prohibited without express consent from the original creators. This software is provided for archival and educational purposes.

All credits and original rights belong to the authors and Gromet's Plaza. The stories remain the copyright property of their respective authors.
