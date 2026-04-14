.PHONY: download convert convert-force build clean all detect fix-broken serve docker-build docker-run docker-run-build sync quick-sync delete-story

PYTHON = python3
PIP = pip3
HUGO = hugo
VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP = $(VENV)/bin/pip

DOCKER_IMAGE = ghcr.io/niobedev/grometsparser:latest
DOCKER_TAG ?= latest
PWD = $(shell pwd)

all: venv download convert build

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	@echo "Setting up virtual environment..."
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	@touch $(VENV)/bin/activate

download: venv
	@echo "Downloading raw HTML stories..."
	$(VENV_PYTHON) download_stories.py

convert: venv
	@echo "Converting stories to website format..."
	$(VENV_PYTHON) convert_to_markdown.py

convert-force: venv
	@echo "Converting all stories to website format (force override)..."
	$(VENV_PYTHON) convert_to_markdown.py --force

build:
	@echo "Building website..."
	cd website && $(HUGO)
	@echo "Creating archive..."
	tar -czf website-archive.tar.gz -C website/public .

clean:
	@echo "Cleaning up..."
	rm -rf $(VENV)
	rm -rf website/public
	rm -rf website/resources
	rm -f website-archive.tar.gz

detect: venv
	@echo "Detecting broken markdown in converted stories..."
	$(VENV_PYTHON) detect_broken_markdown.py

fix-broken: venv
	@echo "Fixing broken markdown (deleting converted files)..."
	$(VENV_PYTHON) detect_broken_markdown.py --delete --force

serve:
	@echo "Starting Hugo development server..."
	cd website && $(HUGO) server --bind 0.0.0.0 --buildDrafts

docker-build:
	@echo "Building Docker image..."
	docker build -t $(DOCKER_IMAGE) .
	docker tag $(DOCKER_IMAGE) ghcr.io/niobedev/grometsparser:$(DOCKER_TAG)

docker-run:
	@echo "Running sync in Docker..."
	docker run --rm \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-v $(PWD):/app \
		$(DOCKER_IMAGE) \
		/bin/bash -c "git fetch && git pull && python3 sync.py"

docker-run-quick:
	@echo "Running quick sync in Docker..."
	docker run --rm \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-v $(PWD):/app \
		$(DOCKER_IMAGE) \
		/bin/bash -c "git fetch && git pull && python3 quick_sync.py"

docker-run-build:
	@echo "Running sync and build in Docker..."
	docker run --rm \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-v $(PWD):/app \
		$(DOCKER_IMAGE) \
		/bin/bash sync_and_build.sh



sync: venv
	@echo "Running sync.py without Docker..."
	GITHUB_TOKEN=$(GITHUB_TOKEN) $(VENV_PYTHON) sync.py

quick-sync: venv
	@echo "Running quick_sync.py without Docker..."
	GITHUB_TOKEN=$(GITHUB_TOKEN) $(VENV_PYTHON) quick_sync.py

delete-story: venv
	@echo "Deleting story from HTML, Markdown, and URLs..."
	@if [ -z "$(URL)" ]; then \
		echo "Usage: make delete-story URL='https://example.com/story.html'"; \
		exit 1; \
	fi
	$(VENV_PYTHON) delete_story.py "$(URL)"
