FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    openssh-client \
    ca-certificates \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sL https://github.com/gohugoio/hugo/releases/download/v0.137.1/hugo_extended_0.137.1_linux-amd64.tar.gz | tar -xz -C /tmp \
    && mv /tmp/hugo /usr/local/bin/hugo \
    && rm -rf /tmp/*

RUN useradd -m -s /bin/bash appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN git submodule update --init --recursive

RUN mkdir -p /var/www

USER appuser

ENV PATH="/app/.venv/bin:${PATH}"

CMD ["python3", "sync.py"]

ENTRYPOINT []