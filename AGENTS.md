# Gromet's Plaza Archive Parser - Agent Instructions

## Key Architecture

- **Two-tier sync strategy**: Quick sync (hourly, checks Updates section only) vs Full sync (weekly, scans all 19 story sites)
- **Makefile-first workflow**: All operations should use `make` commands where possible
- **Docker-native deployment**: Automated sync runs in containers with git commit capabilities
- **Python + Hugo stack**: Python for scraping/processing, Hugo for static site generation

## Critical Commands

### Primary Workflows
```bash
# Quick sync (hourly) - checks only Updates section
make quick-sync          # Local execution
make docker-run-quick    # Docker execution (recommended)

# Full sync (weekly) - scans all story sites  
make sync               # Local execution
make docker-run         # Docker execution (recommended)

# Build static website
make build              # Creates website-archive.tar.gz
```

### Quality Control
```bash
# Check for broken markdown before publishing
make detect             # Detect issues
make fix-broken        # Delete broken files for re-parsing
```

## Docker Requirements

### Volume Mounts
- Always mount project directory: `-v $(pwd):/app`
- Container expects to run at `/app`

### Environment Variables
- `GITHUB_TOKEN`: Required for git commits in sync scripts (must have push access)

### Git Configuration
- Docker image pre-configured with SSH to skip host key verification for GitHub
- Scripts automatically commit and push changes to git

## Project Structure

```
stories/               # Raw HTML files (committed)
website/               # Hugo-based frontend
sync.py               # Full sync script (all story sites)
quick_sync.py         # Quick sync script (Updates section only)
convert_to_markdown.py # Bridge: raw data → Hugo format
download_stories.py   # Scraping engine with 404 tracking
extract_urls.py      # URL discovery (not in Makefile - run manually)
failed_urls.json     # Tracks 404s to avoid redundant requests
```

## Operational Notes

### Sync Behavior
- Scripts automatically detect new stories using MD5 hashing
- Git commits are automatic with descriptive messages (first 5 story titles + count)
- Failed URLs tracked to prevent repeated attempts
- Quick sync preserves/restores original `story_urls.json`

### Docker Build/Deploy
- Docker image builds automatically on git tag push to GitHub Container Registry
- Tag format: `v*` (e.g., `v1.0.0`)
- Available at: `ghcr.io/niobedev/grometsparser:latest` and `ghcr.io/niobedev/grometsparser:v*`

### Prerequisites
- Python 3.x with virtual environment (`make venv` to set up)
- Hugo Extended v0.120+ (included in Docker image)
- Git and GitHub token for automated commits

## Gotchas

- Never run `extract_urls.py` through Makefile - it's a manual operation
- Quick sync only checks the "Updates" section on main.html
- Full sync processes thousands of stories - schedule during low-traffic periods
- Git operations happen inside Docker containers, not on host
- Website serves from `website/public/` after build