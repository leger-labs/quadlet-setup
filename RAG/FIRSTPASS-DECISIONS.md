# Qdrant/RAG Implementation - First Pass Design Decisions

## Overview

This document outlines the design decisions made for implementing Qdrant as the vector database for OpenWebUI's RAG (Retrieval Augmented Generation) functionality.

## Executive Summary

- **Vector Database**: Qdrant (replacing default ChromaDB)
- **Architecture**: Standalone container on llm.network
- **Access**: Internal-only by default, optional dashboard exposure
- **Integration**: OpenWebUI configured via environment variables

## Why Qdrant?

Based on extensive research from user testimonials and technical analysis (documented in `/RAG/README.md` and `/RAG/conundrum.md`), Qdrant was chosen over alternatives for the following reasons:

### Qdrant Advantages
1. **Performance**: Users consistently report better retrieval quality compared to ChromaDB
2. **Stability**: Fewer version compatibility issues than ChromaDB (which had severe issues in recent updates)
3. **Professional Features**: Built-in web dashboard for collection management and verification
4. **Simplicity**: Easier setup than PostgreSQL with pgvector extension
5. **User Preference**: Community consensus favors Qdrant for production use

### Alternatives Considered

**ChromaDB (Default)**
- ❌ Severe performance degradation in recent versions
- ❌ Version compatibility breaking changes
- ❌ Installation challenges on some platforms
- ✅ Default option (simplest if it worked)

**PostgreSQL + pgvector**
- ❌ Complex setup requiring manual schema creation
- ❌ Missing documentation for table structures
- ❌ Pool size configuration limitations
- ✅ Enterprise-grade features
- ✅ Good for existing PostgreSQL infrastructure

**Qdrant (Selected)**
- ✅ Better retrieval performance
- ✅ Web UI for verification
- ✅ Production-ready stability
- ✅ Simple environment variable configuration
- ✅ Active community support

## Architecture Decisions

### 1. Container Isolation
**Decision**: Qdrant runs as a standalone container, not embedded in OpenWebUI

**Rationale**:
- Follows repository principle: "ONE FOLDER PER CONTAINER"
- Allows independent scaling and management
- Enables shared use across multiple services if needed in future
- Separates concerns: OpenWebUI handles UI, Qdrant handles vectors

### 2. Network Configuration
**Decision**: Qdrant runs on `llm.network` with no published port by default

**Rationale**:
- Internal-only access aligns with security best practices
- OpenWebUI accesses via service name: `http://qdrant:6333`
- No external exposure needed for core functionality
- Dashboard port can be optionally exposed via commented line

### 3. Service Naming
**Decision**: Container name is simply `qdrant`, not `openwebui-qdrant`

**Rationale**:
- While OpenWebUI is the primary consumer now, Qdrant could serve other services
- Repository pattern uses shared service names for infrastructure (e.g., `llm-postgres`, `llm-redis`)
- However, being RAG-specific, it's not prefixed with `llm-` like shared databases
- Future services could use the same Qdrant instance with different collections

### 4. Authentication
**Decision**: API key authentication enabled via `QDRANT__SERVICE__API_KEY`

**Rationale**:
- Security by default, even for internal services
- Templated from encrypted secrets: `{{ .api_keys.qdrant }}`
- Prevents unauthorized access if network isolation is compromised
- Aligns with repository security principles

### 5. Storage
**Decision**: Named volume `qdrant.volume` for persistent storage

**Rationale**:
- Follows repository standard for container data persistence
- SELinux labeling with `:Z` flag
- Data survives container updates and restarts
- Consistent with other service volume patterns

### 6. Health Checks
**Decision**: TCP connection test to port 6333

**Rationale**:
- Verifies service is listening and responding
- Uses bash TCP test (standard in Qdrant container)
- 20-second start period allows for initialization
- Consistent with repository health check patterns

### 7. Telemetry
**Decision**: Telemetry disabled via `QDRANT__TELEMETRY_DISABLED=true`

**Rationale**:
- Privacy by default
- Reduces external network calls
- Aligns with local-first architecture
- No external dependencies for core functionality

### 8. Dashboard Exposure (Optional)
**Decision**: Dashboard port commented out by default, easily enabled

**Rationale**:
- Security first: no exposed ports unless needed
- Easy to enable for debugging: uncomment one line
- Could be proxied via Caddy for secure external access if needed
- Follows "NO LOGIN PREFERRED" but allows for monitoring when desired

## Integration with OpenWebUI

### Environment Variables
```bash
VECTOR_DB=qdrant
QDRANT_URI=http://qdrant:6333
QDRANT_API_KEY={{ .api_keys.qdrant }}
```

**Rationale**:
- Uses OpenWebUI's native Qdrant support
- Service name resolution via llm.network
- Templated credentials from encrypted secrets
- No hardcoded values

### Service Dependencies
OpenWebUI container updated with:
- `After=qdrant.service` - Wait for Qdrant to start
- `Wants=qdrant.service` - Request Qdrant runs but don't fail if unavailable

**Rationale**:
- Ensures proper startup order
- Soft dependency (`Wants`) allows OpenWebUI to start even if Qdrant fails
- Follows systemd best practices for service orchestration

## Configuration Management

### Templating Strategy
All configuration driven by `.chezmoi.yaml.tmpl`:

```yaml
ports:
  qdrant: 6333       # Internal API port
  qdrant_grpc: 6334  # gRPC port (internal only)

published_ports:
  qdrant: 6333       # Optional dashboard (commented by default)

api_keys:
  qdrant: "{{ .secrets.api_keys.qdrant }}"
```

**Rationale**:
- Single source of truth for all configuration
- Easy to change ports if needed
- Credentials encrypted in `encrypted_private_secrets.yaml`
- Consistent with repository patterns

### No Hardcoded Values
- All ports: templated from `.chezmoi.yaml.tmpl`
- All credentials: templated from encrypted secrets
- All URLs: use service names on llm.network

**Rationale**:
- Maintainability: change once, apply everywhere
- Security: no credentials in version control
- Flexibility: easy environment-specific configuration

## File Structure

```
containers/systemd/qdrant/
├── qdrant.container.tmpl    # Quadlet definition with templating
├── qdrant.volume            # Volume definition
└── README.md                # Service-specific documentation
```

**Rationale**:
- One folder per container (repository principle)
- Standard naming: `{service}.{type}.tmpl`
- Complete service definition in one place
- Documentation co-located with implementation

## Deployment Considerations

### Startup Order
1. `llm.network` (shared infrastructure)
2. `qdrant` (vector database)
3. `openwebui` (requires Qdrant for RAG)

**Rationale**:
- Network must exist before containers join
- Qdrant must be available before OpenWebUI attempts RAG operations
- Declared via systemd `After=` directives

### Resource Requirements
**Decision**: No resource limits specified in quadlet file

**Rationale**:
- Repository principle: "NO hardware constraints"
- AMD hardware platform handles resource allocation
- Avoids artificial limitations
- Qdrant is lightweight and self-manages resources

### Update Strategy
**Decision**: `AutoUpdate=registry` enabled

**Rationale**:
- Keeps Qdrant up-to-date with latest features
- Security patches applied automatically
- Data persisted in volume survives updates
- Consistent with other service update strategies

## Future Considerations

### Potential Enhancements
1. **Multiple Collections**: Different services could use different collections
2. **Backup Strategy**: Volume backup automation
3. **Replication**: Multi-node Qdrant cluster for high availability
4. **Monitoring**: Prometheus metrics export
5. **Caddy Integration**: Reverse proxy for dashboard with authentication

### Migration Path
If Qdrant proves insufficient:
1. Change `VECTOR_DB` environment variable
2. Deploy alternative vector database container
3. Re-index documents in new database
4. No OpenWebUI code changes needed

## Testing Strategy

### Verification Steps
1. Confirm Qdrant container starts successfully
2. Verify OpenWebUI can connect to Qdrant
3. Upload test document to OpenWebUI
4. Verify collection created in Qdrant (via optional dashboard)
5. Test RAG query retrieves relevant chunks
6. Confirm data persists across container restarts

### Known Limitations
Based on research (`/RAG/README.md`):
1. **Context Window**: Ensure LLM context is ≥8192 tokens (default Ollama 2048 too small)
2. **Chunking**: OpenWebUI's chunking strategy may need tuning per use case
3. **Retrieval Quality**: May need custom RAG templates for optimal results
4. **Full Document Mode**: OpenWebUI's RAG always processes, even in "full context" mode

## Lessons from Research

Key insights from `/RAG/conundrum.md`:

1. **RAG is Mandatory**: OpenWebUI always applies RAG processing, no true bypass
2. **Chunking Limitations**: Arbitrary chunking can break code blocks and context
3. **Workarounds Exist**: Custom pipes can manipulate RAG behavior
4. **Vector DB Matters**: Database choice significantly impacts retrieval quality
5. **Configuration Critical**: Proper settings (context window, chunk size, top-K) essential

## Conclusion

This implementation provides:
- ✅ Production-ready vector database (Qdrant)
- ✅ Secure by default (API key, internal-only)
- ✅ Follows repository architecture principles
- ✅ Maintainable configuration (all templated)
- ✅ Room for future enhancements
- ✅ Well-documented for operators

The design balances simplicity, security, and flexibility while adhering to the repository's strict architectural requirements.

## References

- [OpenWebUI Qdrant Documentation](https://docs.openwebui.com/features/rag/)
- `/RAG/README.md` - User testimonials and technical analysis
- `/RAG/conundrum.md` - Deep dive into OpenWebUI RAG challenges
- `/RAG/qdrant-compose.md` - Docker Compose examples
- `/inspiration/harbor/compose.qdrant.yml` - Reference implementation
- `CLAUDE.md` - Repository architecture principles
- `resources.md` - Network architecture and patterns
