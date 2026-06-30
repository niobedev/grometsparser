# Gromet's Plaza Archive

![Build and Publish](https://github.com/niobedev/grometsparser/actions/workflows/build-and-publish.yml/badge.svg)
![Hourly Sync](https://github.com/niobedev/grometsparser/actions/workflows/hourly-sync.yml/badge.svg)
![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)

A self-updating, serverless web archive of stories from [Gromet's Plaza](https://grometsplaza.net/).

**Live Website:** https://plaza.housetoral.uk

> This site contains adult content intended for mature audiences only.

## Features

- **Automatic Updates** - Checks for new stories every hour via GitHub Actions
- **Matrix Notifications** - Posts new story announcements to Matrix rooms
- **Fast Search** - Client-side Fuse.js search across story titles, authors, and tags
- **Responsive** - Clean, mobile-friendly design
- **Rich Metadata** - Browse by tags, authors, or use the search
- **Serverless** - Runs entirely on GitHub's infrastructure
- **Versioned Releases** - Every update creates a downloadable archive

## How It Works

1. **Hourly Sync** - GitHub Actions runs `quick_sync.py` every hour
2. **Check Updates** - Parses the "Updates" section on grometsplaza.net
3. **Download New Stories** - Only fetches stories not already in the archive
4. **Convert to Markdown** - Transforms raw HTML to Hugo markdown
5. **Build Website** - Generates static HTML with Hugo
6. **Deploy** - Pushes to GitHub Pages (https://plaza.housetoral.uk)
7. **Notify** - Sends new story list with links to Matrix
8. **Release** - Creates a GitHub Release with the archive

No servers, no cron jobs, no manual intervention required.

## Project Structure

```
.env                    # Environment variables (GITHUB_TOKEN) - not committed
stories/                # Raw HTML from grometsplaza.net
website/                # Hugo static site
  content/stories/      # Markdown stories
  layouts/              # Custom templates
  public/               # Built site (auto-generated)
quick_sync.py           # Hourly sync script (Updates section only)
sync.py                 # Full sync script (all story sites)
download_stories.py     # Story downloader
convert_to_markdown.py  # HTML to Markdown converter
extract_urls.py         # URL discovery (manual operation)
format_matrix_message.py # Matrix notification formatter
delete_story.py         # Story deletion utility
story_urls.json         # Story URL database
failed_urls.json        # Tracks 404s to avoid redundant requests
deploy.sh               # VPS deployment script
docker-run.sh           # Docker entrypoint for full sync
docker-run-quick.sh     # Docker entrypoint for quick sync
.github/workflows/
  build-and-publish.yml # Runs on push to main
  hourly-sync.yml       # Runs every hour
```

## Development

### Prerequisites

- Python 3.12+
- Hugo Extended 0.146+

### Local Setup

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/niobedev/grometsparser.git
cd grometsparser

# Set up virtual environment
make venv

# Run quick sync
make quick-sync

# Build website
make build

# Serve locally
make serve
```

### Docker

```bash
# Build image (for x86_64 servers)
make docker-build DOCKER_ARCH=amd64

# Run quick sync in Docker
make docker-run-quick

# Run full sync in Docker
make docker-run
```

### Environment Variables

Create a `.env` file (automatically loaded by Makefile):

```bash
GITHUB_TOKEN=your_github_token  # Required for commits in Docker
DOCKER_ARCH=amd64               # arm64 for Apple Silicon
```

### Quality Control

```bash
make detect        # Detect broken markdown files
make fix-broken    # Delete broken files for re-parsing
```

## Deployment

### GitHub Pages (Default)

The website automatically deploys to https://plaza.housetoral.uk via GitHub Actions.

### VPS Deployment

Download the latest release and deploy:

```bash
ARCHIVE_URL=$(curl -s https://api.github.com/repos/niobedev/grometsparser/releases/latest | grep -o '"browser_download_url": "[^"]*' | cut -d'"' -f4)
wget $ARCHIVE_URL -O website.tar.gz
tar -xzf website.tar.gz
cp -r public/* /var/www/gromets/
```

Or use the deployment script:

```bash
./deploy.sh
```

## GitHub Actions

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `hourly-sync.yml` | Every hour + manual | Check for new stories, build, deploy, notify Matrix |
| `build-and-publish.yml` | Push to main | Full rebuild, create release |

## License

This project is licensed under the [BSD-3-Clause License](LICENSE).

**Stories are copyrighted by their respective authors.** This software is provided for archival purposes only. All rights belong to the original authors and Gromet's Plaza.
