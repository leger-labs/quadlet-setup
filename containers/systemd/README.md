# Container Services

This directory contains Podman Quadlet configurations for all container services, organized following the "one folder per container" architecture.

## Architecture Overview

All services communicate via the shared `llm.network` (10.89.0.0/24 subnet) using container names as DNS. External access is handled through Caddy reverse proxy with Tailscale URLs.

## Network Structure

```
External (Tailscale) → Caddy (Host) → Published Ports → Container Network (llm.network)
```

### Three Network Layers

1. **Tailscale Network**: Secure remote access via `*.your-tailnet.ts.net`
2. **Caddy Proxy**: Routes Tailscale URLs to localhost published ports
3. **llm.network**: Container-to-container communication by service name

## Core Services

### LiteLLM (`litellm/`)
- **Purpose**: Unified LLM proxy for OpenAI, Anthropic, Google APIs
- **Port**: 4000 (internal) → 4000 (published)
- **Dependencies**: litellm-postgres, litellm-redis
- **Access**: `http://litellm:4000` (internal), Caddy proxies external

### Open WebUI (`openwebui/`)
- **Purpose**: Main chat interface (ChatGPT-like UI)
- **Port**: 8080 (internal) → 3000 (published)
- **Dependencies**: openwebui-postgres, openwebui-redis, litellm, searxng, docling
- **Access**: `http://openwebui:8080` (internal), Caddy proxies external
- **Auth**: Disabled by default for local use

### SearXNG (`searxng/`)
- **Purpose**: Privacy-respecting metasearch engine
- **Port**: 8080 (internal) → 8888 (published)
- **Dependencies**: searxng-redis
- **Access**: `http://searxng:8080` (internal), Caddy proxies external

### Docling (`docling/`)
- **Purpose**: Document processing and content extraction
- **Port**: 5001 (internal) → 5001 (published)
- **Dependencies**: None
- **Access**: `http://docling:5001` (internal)

## Auxiliary Services (Internal Only)

These services have **NO published ports** - they're only accessible within the llm.network:

- **litellm-postgres**: Database for LiteLLM (`litellm-postgres:5432`)
- **litellm-redis**: Cache for LiteLLM (`litellm-redis:6379`)
- **openwebui-postgres**: Database for Open WebUI (`openwebui-postgres:5432`)
- **openwebui-redis**: Cache for Open WebUI (`openwebui-redis:6379`)
- **searxng-redis**: Cache for SearXNG (`searxng-redis:6379`)

## Service Isolation Principles

Per CLAUDE.md guidelines:
- **ONE FOLDER PER CONTAINER** - Never combine services
- **Dedicated auxiliary services** - Each main service gets its own postgres/redis (not shared)
- **Unique container names** - e.g., `litellm-redis`, `openwebui-redis` (not just `redis`)

## Configuration Management

All configuration is driven by `.chezmoi.yaml.tmpl`:
- Port numbers (`{{ .ports.service }}`, `{{ .published_ports.service }}`)
- API keys (`{{ .api_keys.provider }}`)
- Database credentials (`{{ .database.* }}`)
- URLs (`{{ .urls.service }}`)

## File Structure

Each service folder contains:
```
service-name/
├── service-name.container     # Quadlet definition
├── service-name.volume        # Volume definition (if needed)
├── service-name.env.tmpl      # Environment file (if complex)
└── README.md                  # Service documentation
```

## Shared Infrastructure

- **llm.network** - Top-level network file (not in a service folder)
- All services connect to this network
- Provides DNS resolution by container name

## Testing

```bash
# Check network exists
podman network ls | grep llm

# Test container communication
podman exec openwebui curl http://litellm:4000/health
podman exec openwebui curl http://searxng:8080

# Check service status
systemctl --user status litellm openwebui searxng docling
```

## Important Notes

- **NO NVIDIA configurations** - This runs on AMD hardware only
- **NO hardware constraints** - No disk, memory, or GPU specifications
- **NO LOGIN by default** - Local services run without authentication
- All services use `WantedBy=scroll-session.target`
- Health checks are defined for all services
