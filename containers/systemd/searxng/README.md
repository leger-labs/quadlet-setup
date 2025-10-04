# SearXNG Service

SearXNG is a privacy-respecting metasearch engine that aggregates results from multiple search engines.

## Components

- **searxng.container** - Main SearXNG service
- **searxng.volume** - Volume for configuration and data
- **searxng-redis/** - Dedicated Redis cache for SearXNG

## Network Architecture

- **Internal Port**: 8080
- **Published Port**: 8888 (for Caddy)
- **Network**: llm.network
- **Dependencies**: searxng-redis

## Service Communication

SearXNG connects to:
- `searxng-redis:6379` - Cache for search results

Other services connect to SearXNG via:
- `searxng:8080` (within llm.network)

## Configuration

All configuration is templated via chezmoi from `.chezmoi.yaml.tmpl`:
- Base URL
- Redis connection
- Instance name

## Integration

Open WebUI uses SearXNG for RAG web search functionality via:
`SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>`

## Health Check

Endpoint: `http://localhost:8080`
