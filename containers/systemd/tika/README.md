# Apache Tika - Content Extraction Service

## Overview

Apache Tika is a content detection and analysis framework for extracting metadata and text from various document formats. It's used as an alternative or complement to Mistral OCR for local document processing.

## Architecture

- **Container**: `tika`
- **Network**: `llm.network` (10.89.0.0/24)
- **Internal Port**: 9998
- **Published Port**: None (internal only)
- **Image**: `docker.io/apache/tika:latest-full`

## Service Communication

Tika is accessed internally by OpenWebUI for document extraction:

```
OpenWebUI → http://tika:9998
```

## Configuration

The service runs with 2GB heap memory for document processing. Configuration is done via environment variables in the container file.

## Usage

Referenced in OpenWebUI environment as:
```bash
TIKA_SERVER_URL=http://tika:9998
```

## Health Check

The service provides a health endpoint at `/tika` that returns service status.
