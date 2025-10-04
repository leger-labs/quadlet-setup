# Letta - Memory Management Service

## Overview

Letta is a memory management service for LLM applications, providing persistent conversational memory without MCP server management. It's configured specifically for memory-only functionality, integrated with OpenWebUI.

## Architecture

- **Container**: `letta`
- **Network**: `llm.network` (10.89.0.0/24)
- **Internal Port**: 8283
- **Published Port**: 8283 (for Caddy proxy)
- **Image**: `docker.io/letta/letta:latest`
- **Database**: Dedicated `letta-postgres` instance

## Service Communication

Letta communicates with other services on the llm.network:

```
OpenWebUI → http://letta:8283 (memory queries)
Letta → http://litellm:4000 (LLM inference)
Letta → postgresql://letta-postgres:5432/letta (memory storage)
```

External access via Caddy:
```
https://letta.hostname.tailnet.ts.net → localhost:8283 → letta:8283
```

## Configuration

Letta is configured with:
- **Memory management only** - MCP server management is disabled
- **No authentication** - Suitable for local/private deployments
- **LiteLLM integration** - Uses litellm for LLM and embedding endpoints
- **Dedicated postgres** - Isolated database for memory persistence

### Environment Variables

See `letta.env.tmpl` for full configuration:
- `LETTA_MCP_ENABLED=false` - Disables MCP management
- `LETTA_AUTH_ENABLED=false` - No authentication for local use
- Database connection to dedicated postgres instance
- LLM/embedding endpoints pointing to litellm

## Usage in OpenWebUI

Reference in OpenWebUI pipelines or tools:
```python
LETTA_API_BASE=http://letta:8283
```

## Reference Implementation

Based on:
- https://docs.letta.com/guides/server/remote
- https://github.com/wsargent/recipellm (usage example)
- https://github.com/letta-ai/letta

## Database

Letta uses a dedicated PostgreSQL instance (`letta-postgres`) for memory storage:
- **No published ports** - Internal access only
- **Database name**: `letta`
- **Volume**: Persistent storage for conversation memory
