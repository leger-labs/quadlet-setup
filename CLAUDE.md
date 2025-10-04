# Claude Code GitHub Actions Instructions

## Repository Overview

This repository provides chezmoi-templatable Podman Quadlet configurations for a comprehensive container-based service stack. Each container service is defined in its own folder with full chezmoi templating support.

## Core Architecture Principles

### Network Configuration
- All services connect to a shared `llm.network` subnet (10.89.0.0/24)
- Services communicate using container names as DNS (e.g., `http://litellm:4000`)
- External access is handled through Caddy reverse proxy with Tailscale URLs

### Service Isolation
- **ONE FOLDER PER CONTAINER** - Never combine services
- Each service that needs auxiliary services (Redis, PostgreSQL) gets its own dedicated instances
- Example: `openwebui` gets `openwebui-redis` and `openwebui-postgres`, NOT shared services
- Container names must be unique and descriptive (e.g., `litellm-redis`, not just `redis`)

### Chezmoi Templating
- All configuration is driven by `.chezmoi.yaml.tmpl`
- Use `{{ .variable }}` syntax for all dynamic values
- Port numbers come from the master config, never hardcoded
- API keys and secrets are templated from encrypted storage
- Environment files use `.env.tmpl` or direct templating in `.container` files

## Mandatory Requirements

### Hardware & Platform
- **NO NVIDIA configurations** - This runs on AMD hardware only
- **NO hardware constraints** - No disk size, memory allocation, or GPU specifications in quadlet files
- **NO compute unit specifications** - The platform handles this automatically

### Authentication & Security
- **NO LOGIN PREFERRED** - Disable authentication where possible for local services
- When auth is required, template credentials from encrypted secrets
- Use `WEBUI_AUTH=false` or equivalent for local-only services

### File Structure
Each container implementation must include:
```
container-name/
├── container-name.container      # Quadlet definition
├── container-name.volume         # Volume definition (if needed)
├── container-name.env.tmpl       # Environment variables (if complex)
└── README.md                     # Service-specific documentation
```

For auxiliary services:
```
container-name/
├── container-name.container
├── container-name-redis.container
├── container-name-redis.volume
├── container-name-postgres.container
├── container-name-postgres.volume
└── container-name.env.tmpl
```

### Quadlet File Standards

#### [Unit] Section
```ini
[Unit]
Description=Clear description of service
After=network-online.target llm.network.service
Requires=llm.network.service
Wants=dependency1.service dependency2.service
```

#### [Container] Section
```ini
[Container]
Image=registry.example.com/image:tag
AutoUpdate=registry
ContainerName=unique-descriptive-name
Network=llm.network
PublishPort={{ .published_ports.service }}:{{ .ports.service }}
Volume=service-name.volume:/data:Z
Environment=KEY=value
EnvironmentFile=%h/.config/containers/service.env
HealthCmd="command to check health"
HealthInterval=30s
HealthTimeout=5s
HealthRetries=3
HealthStartPeriod=10s
```

#### [Service] Section
```ini
[Service]
Slice=llm.slice
TimeoutStartSec=900
Restart=on-failure
RestartSec=10
```

#### [Install] Section
```ini
[Install]
WantedBy=scroll-session.target
```

### Port Configuration
- **Published ports** (host:container): Only when Caddy needs to proxy to it
- **Internal-only services**: No `PublishPort` directive (e.g., postgres, redis for backend only)
- Port numbers come from `.chezmoi.yaml.tmpl`:
  - `{{ .ports.service }}` - Internal container port
  - `{{ .published_ports.service }}` - Host published port

### Environment Variables
- Simple configs: Use `Environment=` directly in `.container` file
- Complex configs: Use `EnvironmentFile=%h/.config/containers/service.env`
- Always template sensitive values: `{{ .api_keys.provider }}`
- Reference other services by container name: `DATABASE_URL=postgresql://user:pass@service-postgres:5432/db`

### Health Checks
Every service must include:
```ini
HealthCmd="service-specific-health-check"
HealthInterval=30s
HealthTimeout=5s
HealthRetries=3
HealthStartPeriod=10s
```

### Volumes
- Named volumes: Create separate `.volume` file
- Bind mounts: Use `%h` for home directory paths
- Always use `:Z` for SELinux labeling on named volumes
- Use `:ro,Z` for read-only mounts

## Docker Compose to Quadlet Conversion

When converting from docker-compose:
1. Each `service:` becomes a separate `.container` file
2. `ports:` → `PublishPort=` (only if external access needed)
3. `volumes:` → `Volume=` (create `.volume` files for named volumes)
4. `environment:` → `Environment=` or `EnvironmentFile=`
5. `depends_on:` → `After=` and `Wants=` in `[Unit]` section
6. `networks:` → `Network=llm.network` (all services)

## Testing & Validation

Before marking an issue complete:
1. Verify file exists in correct folder structure
2. Confirm all template variables are defined in `.chezmoi.yaml.tmpl`
3. Check health checks are appropriate for the service
4. Validate service dependencies are correctly declared
5. Ensure no hardcoded values (ports, passwords, URLs)

## Common Patterns

### Database Service
```ini
[Container]
Image=docker.io/postgres:16
ContainerName=service-postgres
Network=llm.network
# NO PublishPort - internal only
Environment=POSTGRES_USER={{ .database.user }}
Environment=POSTGRES_PASSWORD={{ .database.password }}
Volume=service-postgres.volume:/var/lib/postgresql/data:Z
```

### Cache Service
```ini
[Container]
Image=docker.io/redis:latest
ContainerName=service-redis
Network=llm.network
# NO PublishPort - internal only
Volume=service-redis.volume:/data:Z
```

### Web Service
```ini
[Container]
Image=ghcr.io/project/image:latest
ContainerName=service
Network=llm.network
PublishPort={{ .published_ports.service }}:{{ .ports.service }}
Environment=DATABASE_URL=postgresql://user:pass@service-postgres:5432/db
Environment=REDIS_URL=redis://service-redis:6379
```

## What NOT to Include

- Hardware specifications (CPU, RAM, GPU)
- NVIDIA/CUDA configurations
- Resource limits or reservations
- Hardcoded ports, URLs, or credentials
- Shared auxiliary services across multiple main services
- Authentication when not required
- References to Windows or Docker Desktop

## Final Checklist

- [ ] One folder per container service
- [ ] All ports from `.chezmoi.yaml.tmpl`
- [ ] All secrets templated from encrypted storage
- [ ] Service uses `llm.network`
- [ ] Health check defined
- [ ] Dependencies declared in `[Unit]`
- [ ] No NVIDIA configurations
- [ ] No hardware constraints
- [ ] Auxiliary services are service-specific (not shared)
- [ ] Container names are unique and descriptive
