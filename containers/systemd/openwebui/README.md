# Open WebUI Service

Open WebUI is the main user interface for interacting with LLMs, providing a ChatGPT-like experience.

## Components

- **openwebui.container** - Main Open WebUI service
- **openwebui.volume** - Volume for user data and uploads
- **openwebui.env.tmpl** - Environment configuration file
- **openwebui-postgres/** - Dedicated PostgreSQL database with pgvector
- **openwebui-redis/** - Dedicated Redis cache

## Network Architecture

- **Internal Port**: 8080
- **Published Port**: 3000 (for Caddy)
- **Network**: llm.network
- **Dependencies**: litellm, openwebui-postgres, openwebui-redis, searxng, docling

## Service Communication

Open WebUI connects to:
- `openwebui-postgres:5432` - Database for user data, chats, etc.
- `openwebui-redis:6379` - Cache for sessions and temporary data
- `litellm:4000` - LLM proxy for AI responses
- `searxng:8080` - Web search for RAG
- `docling:5001` - Document processing

## Configuration

All configuration is templated via chezmoi from `.chezmoi.yaml.tmpl`:
- Database connection
- Redis connection
- LiteLLM API endpoint
- SearXNG endpoint
- Docling endpoint
- Authentication settings (disabled by default per CLAUDE.md)

## Authentication

Per CLAUDE.md guidelines, authentication is **disabled by default** (`WEBUI_AUTH=false`) for local-only services.

## Health Check

Endpoint: `http://localhost:8080/health`
