FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg debian-keyring debian-archive-keyring \
        apt-transport-https tini \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
        | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg \
    && curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
        > /etc/apt/sources.list.d/caddy-stable.list \
    && apt-get update && apt-get install -y --no-install-recommends caddy \
    && apt-get purge -y curl gnupg apt-transport-https \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# paper-search-mcp PyPI v0.1.3 doesn't have GOOGLE_SCHOLAR_PROXY_URL support yet — install from GitHub main
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && pip install --no-cache-dir \
        "paper-search-mcp @ git+https://github.com/openags/paper-search-mcp.git@main" \
        mcp-proxy==0.11.0 \
    && apt-get purge -y git \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY Caddyfile.template /app/Caddyfile.template
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8080

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/start.sh"]
