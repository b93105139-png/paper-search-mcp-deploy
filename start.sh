#!/bin/bash
set -euo pipefail

: "${BEARER_TOKEN:?BEARER_TOKEN env var is required}"

# Render Caddyfile from template (substitute token into URL path matcher)
sed "s|__BEARER_TOKEN__|${BEARER_TOKEN}|g" /app/Caddyfile.template > /app/Caddyfile

# Start mcp-proxy in background, exposing paper-search-mcp via streamable HTTP on :8081
mcp-proxy \
	--host 127.0.0.1 \
	--port 8081 \
	--pass-environment \
	--stateless \
	--allow-origin '*' \
	-- python -m paper_search_mcp.server &

MCP_PID=$!
trap "kill ${MCP_PID} 2>/dev/null || true" EXIT

# Wait briefly for mcp-proxy to bind
sleep 2

# Foreground: Caddy proxies /<TOKEN>/* → :8081 (token stripped)
exec caddy run --config /app/Caddyfile --adapter caddyfile
