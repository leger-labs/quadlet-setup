# Qdrant Vector Database

Qdrant is a high-performance vector database used by OpenWebUI for Retrieval Augmented Generation (RAG) functionality.

## Purpose

- Stores document embeddings for semantic search
- Provides fast vector similarity search for RAG queries
- Replaces the default ChromaDB with better performance and reliability

## Configuration

- **Container Name**: `qdrant`
- **Internal Port**: 6333 (HTTP API), 6334 (gRPC)
- **Network**: `llm.network` (internal only)
- **Volume**: `qdrant.volume` → `/qdrant/storage`

## Network Architecture

Qdrant runs **internal-only** on the `llm.network`:
- OpenWebUI connects via: `http://qdrant:6333`
- No external access required
- Optional dashboard can be enabled by uncommenting PublishPort in `.container.tmpl`

## Integration

OpenWebUI is configured to use Qdrant through environment variables:
- `VECTOR_DB=qdrant`
- `QDRANT_URI=http://qdrant:6333`
- `QDRANT_API_KEY={{ .api_keys.qdrant }}`

## Security

- API key authentication enabled
- Telemetry disabled for privacy
- Internal-only access via llm.network

## Monitoring

To enable the web dashboard (optional):
1. Uncomment the `PublishPort` line in `qdrant.container.tmpl`
2. Access at: `http://localhost:6333/dashboard`
3. Or configure Caddy reverse proxy for external access

## Storage

All vector data is persisted in the `qdrant-storage` volume, ensuring data survives container restarts.

## Health Check

Uses TCP connection test to port 6333 to verify service availability.
