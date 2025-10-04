# LiteLLM Service

LiteLLM is a proxy service that provides a unified API interface for multiple LLM providers (OpenAI, Anthropic, Google, etc.).

## Components

- **litellm.container** - Main LiteLLM proxy service
- **litellm.yaml.tmpl** - Configuration file defining available models
- **litellm-postgres/** - Dedicated PostgreSQL database for LiteLLM
- **litellm-redis/** - Dedicated Redis cache for LiteLLM

## Network Architecture

- **Internal Port**: 4000
- **Published Port**: 4000 (for Caddy)
- **Network**: llm.network
- **Dependencies**: litellm-postgres, litellm-redis

## Service Communication

LiteLLM connects to:
- `litellm-postgres:5432` - Database for logging and config
- `litellm-redis:6379` - Cache for responses

Other services connect to LiteLLM via:
- `litellm:4000` (within llm.network)

## Configuration

All configuration is templated via chezmoi from `.chezmoi.yaml.tmpl`:
- API keys for providers
- Database connection string
- Redis connection details
- Master key for authentication

## Health Check

Endpoint: `http://localhost:4000/health/readiness`
