FROM python:3.12-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG HUGO_ARCH=amd64

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    openssh-client \
    ca-certificates \
    make \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sL https://github.com/gohugoio/hugo/releases/download/v0.146.6/hugo_extended_0.146.6_linux-${HUGO_ARCH}.tar.gz | tar -xz -C /tmp \
    && mv /tmp/hugo /usr/local/bin/hugo \
    && rm -rf /tmp/*

# Configure SSH to skip host key verification for GitHub
RUN mkdir -p /root/.ssh && \
    echo "Host github.com" >> /root/.ssh/config && \
    echo "  StrictHostKeyChecking no" >> /root/.ssh/config && \
    echo "  UserKnownHostsFile /dev/null" >> /root/.ssh/config

# Configure git for automated commits
RUN git config --global user.name "Gromets Parser" && \
    git config --global user.email "parser@grometsplaza.net"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

CMD ["/bin/bash", "daily_sync.sh"]