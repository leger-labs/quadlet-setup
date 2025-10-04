# Docling Service

Docling is a document processing service for converting and extracting content from various document formats.

## Components

- **docling.container** - Main Docling service

## Network Architecture

- **Internal Port**: 5001
- **Published Port**: 5001 (for Caddy, optional)
- **Network**: llm.network
- **Dependencies**: None

## Service Communication

Other services connect to Docling via:
- `docling:5001` (within llm.network)

## Configuration

Minimal configuration required - uses default settings.

## Integration

Open WebUI uses Docling for document content extraction via:
`DOCLING_SERVER_URL=http://docling:5001`

## Health Check

Endpoint: `http://localhost:5001/health`
