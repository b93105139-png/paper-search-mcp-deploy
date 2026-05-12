# paper-search-mcp-deploy

Remote HTTP MCP wrapper for [paper-search-mcp](https://github.com/openags/paper-search-mcp).

Deploys to Zeabur, exposed at `https://paper-search.jessefang.com/mcp` with Bearer auth. Routes Google Scholar requests through ScraperAPI to bypass datacenter IP blocks.

## Architecture

```
HTTPS → Zeabur edge → Caddy (:8080, Bearer auth)
                   → mcp-proxy (:8081, stdio↔streamable_http)
                   → paper-search-mcp (stdio subprocess)
                   → arXiv / PubMed / bioRxiv / medRxiv (direct)
                   → Google Scholar (via ScraperAPI proxy)
```

## Required env vars (set in Zeabur dashboard)

| Var | Purpose |
|-----|---------|
| `BEARER_TOKEN` | Random 32+ char string. Clients must send `Authorization: Bearer <token>`. |
| `PAPER_SEARCH_MCP_GOOGLE_SCHOLAR_PROXY_URL` | `http://scraperapi:<KEY>@proxy-server.scraperapi.com:8001` |

## Endpoints

- `GET /healthz` — public, returns `OK 200`
- `* /mcp` — Bearer-protected, MCP streamable HTTP
- `* /sse` — Bearer-protected, MCP SSE (legacy)

## Local test

```bash
docker build -t paper-search-mcp-deploy .
docker run --rm -p 8080:8080 \
    -e BEARER_TOKEN=test \
    -e PAPER_SEARCH_MCP_GOOGLE_SCHOLAR_PROXY_URL='http://...' \
    paper-search-mcp-deploy
curl http://localhost:8080/healthz   # → OK
```
