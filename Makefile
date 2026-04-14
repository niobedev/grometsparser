-include .env
.PHONY: download convert convert-force build clean all detect fix-broken serve docker-build docker-run sync quick-sync delete-story

PYTHON = python3
PIP = pip3
VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP = $(VENV)/bin/pip

DOCKER_IMAGE = grometsparser:local
DOCKER_TAG ?= latest
DOCKER_ARCH ?= amd64
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
	@echo "Building website in Docker..."
	docker run --rm \
		-v $(PWD):/app \
		$(DOCKER_IMAGE) \
		/bin/bash -c "cd /app/website && hugo"

serve:
	@echo "Starting Hugo development server in Docker..."
	docker run --rm -it \
		-p 1313:1313 \
		-v $(PWD):/app \
		$(DOCKER_IMAGE) \
		/bin/bash -c "cd /app/website && hugo server --bind 0.0.0.0 --buildDrafts"

docker-build:
	@echo "Building Docker image for $(DOCKER_ARCH)..."
	docker build --build-arg HUGO_ARCH=$(DOCKER_ARCH) -t $(DOCKER_IMAGE) .
	docker tag $(DOCKER_IMAGE) ghcr.io/niobedev/grometsparser:$(DOCKER_TAG)

docker-run:
	@docker run --rm \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-v $(PWD):/app \
		$(DOCKER_IMAGE) \
		/app/docker-run.sh

docker-run-quick:
	@docker run --rm \
		-e GITHUB_TOKEN=$(GITHUB_TOKEN) \
		-v $(PWD):/app \
		$(DOCKER_IMAGE) \
		/app/docker-run-quick.sh
