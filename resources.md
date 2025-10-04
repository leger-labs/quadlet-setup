Previous output of claude llm scoping, resulting spec below

# Organized Container Structure + Network Architecture

## Part 1: Proper Folder Structure

### The New Organization

```
~/.local/share/chezmoi/
│
├── .chezmoi.yaml.tmpl                    ⭐ MASTER CONFIG
├── encrypted_private_secrets.yaml        🔒 ALL SECRETS
│
├── private_dot_local/
│   └── private_share/
│       └── private_applications/         → ~/.local/share/applications/
│           ├── openwebui.desktop.tmpl    (URL points to {{ .urls.openwebui }})
│           ├── litellm.desktop.tmpl      (URL points to {{ .urls.litellm }})
│           ├── cockpit.desktop.tmpl
│           ├── searxng.desktop.tmpl
│           └── nextcloud.desktop.tmpl
│
├── private_dot_config/
│   │
│   ├── caddy/
│   │   └── Caddyfile.tmpl                ⭐ REVERSE PROXY
│   │
│   ├── cockpit/
│   │   └── cockpit.conf.tmpl
│   │
│   ├── sway/
│   │   └── config.tmpl                   (keybinds reference {{ .urls.* }})
│   │
│   └── containers/
│       │
│       └── systemd/                      → ~/.config/containers/systemd/
│           │
│           ├─── 📁 SHARED INFRASTRUCTURE (top level) ───
│           │
│           ├── llm.network               ⭐ SHARED NETWORK (static)
│           │   └─ All containers connect to this
│           │
│           ├── llm.env.tmpl              (optional: shared env vars)
│           │
│           ├─── 📁 SERVICE FOLDERS (one per service) ───
│           │
│           ├── openwebui/                ⭐ OPENWEBUI SERVICE
│           │   ├── openwebui.container.tmpl
│           │   ├── openwebui.volume
│           │   └── openwebui.env.tmpl    (service-specific config)
│           │
│           ├── litellm/                  ⭐ LITELLM SERVICE
│           │   ├── litellm.container.tmpl
│           │   └── litellm.yaml.tmpl     (service-specific config)
│           │
│           ├── llm-postgres/             ⭐ POSTGRES DATABASE
│           │   ├── llm-postgres.container.tmpl
│           │   └── llm-postgres.volume
│           │
│           ├── llm-redis/                ⭐ REDIS CACHE
│           │   ├── llm-redis.container.tmpl
│           │   └── llm-redis.volume
│           │
│           ├── searxng/                  ⭐ SEARCH ENGINE
│           │   ├── searxng.container.tmpl
│           │   ├── searxng.volume
│           │   └── searxng-settings.yml.tmpl
│           │
│           ├── docling/                  ⭐ DOCUMENT PROCESSOR
│           │   └── docling.container.tmpl
│           │
│           ├── tika/                     ⭐ CONTENT EXTRACTION
│           │   └── tika.container.tmpl
│           │
│           ├── mcp/                      ⭐ TOOL SERVER
│           │   ├── mcp.container.tmpl
│           │   └── mcp-config.json.tmpl
│           │
│           └── user/                     → ~/.config/containers/systemd/user/
│               ├── nextcloud/
│               │   └── nextcloud.container.tmpl
│               └── whisper/
│                   └── whisper-npu.container.tmpl
│
└── run_once_after/
    ├── 01-setup-tailscale.sh.tmpl
    ├── 02-setup-cockpit.sh.tmpl
    └── 03-reload-systemd.sh.tmpl
```

### Key Changes:

1. ✅ **Each service gets its own folder**
   - Makes organization clear
   - Easy to find related files
   - Can add README.md per service

2. ✅ **Desktop files are templates** (not auto-generated)
   - One .desktop.tmpl per webapp
   - References {{ .urls.* }} from master config
   - Simple and maintainable

3. ✅ **Shared infrastructure at top level**
   - `llm.network` - network all containers use
   - `llm.env.tmpl` - optional shared env vars

---

## Part 2: Network Architecture Explained

### Three Network Layers

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: External Access (Tailscale)                        │
│ Purpose: Secure remote access to your services              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User's Device (anywhere on Tailnet)                        │
│         │                                                    │
│         │ HTTPS over Tailscale VPN                          │
│         ↓                                                    │
│  https://ai.llm-server.your-tailnet.ts.net                 │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ LAYER 2: Host Proxy (Caddy)                                 │
│ Purpose: Route external requests to local services          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Caddy (port 443)                                           │
│    ├─ ai.hostname.tailnet → localhost:3000                 │
│    ├─ litellm.hostname.tailnet → localhost:4000            │
│    └─ search.hostname.tailnet → localhost:8888             │
│                                                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ localhost published ports
                       │
┌──────────────────────▼──────────────────────────────────────┐
│ LAYER 3: Container Network (Podman)                         │
│ Purpose: Inter-container communication                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  llm.network (10.89.0.0/24)                                 │
│    │                                                         │
│    ├─ openwebui:8080 ──┬─→ litellm:4000                    │
│    │                    ├─→ postgres:5432                   │
│    │                    ├─→ redis:6379                      │
│    │                    ├─→ searxng:8080                    │
│    │                    ├─→ docling:5001                    │
│    │                    └─→ tika:9998                       │
│    │                                                         │
│    ├─ litellm:4000 ─────┬─→ postgres:5432                  │
│    │                     └─→ redis:6379                     │
│    │                                                         │
│    ├─ searxng:8080 ─────→ redis:6379                       │
│    │                                                         │
│    └─ mcp:8000 ─────────→ postgres:5432                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Network Layer Responsibilities:

#### Layer 1: Tailscale (External Network)
- **Protocol:** HTTPS over Tailscale VPN
- **DNS:** MagicDNS resolves `*.your-tailnet.ts.net`
- **Auth:** Tailscale handles authentication
- **Certs:** Tailscale provides TLS certificates
- **Purpose:** Secure external access from anywhere

#### Layer 2: Caddy (Host Proxy)
- **Listens on:** Host ports 80, 443
- **Routes to:** localhost published ports
- **Example:** `ai.hostname.tailnet:443` → `localhost:3000`
- **Purpose:** 
  - Terminate TLS
  - Route to correct service
  - Single entry point
  - Clean URLs

#### Layer 3: Podman Network (Internal)
- **Network:** `llm.network` (10.89.0.0/24)
- **Communication:** Container-to-container by name
- **Example:** `openwebui` → `litellm:4000`
- **Purpose:**
  - Isolated network for containers
  - Service discovery by name
  - No published ports needed for internal communication

---

## Part 3: Where Does llm.network Go?

### Answer: Top Level (Shared Infrastructure)

**Location:**
```
~/.config/containers/systemd/llm.network
```

**Why top level?**
- It's **shared infrastructure**
- All services connect to it
- Not specific to any one service
- Similar to volumes that span services

**Content (`llm.network` - static, not templated):**

```ini
[Network]
NetworkName=llm
Gateway=10.89.0.1
Subnet=10.89.0.0/24
```

**In Chezmoi:**
```
private_dot_config/containers/systemd/llm.network
```
(No .tmpl extension - this is a static file)

---

## Part 4: Complete Network Flow Example

### User Accesses OpenWebUI:

```
1. User types: https://ai.llm-server.your-tailnet.ts.net
   └─ Tailscale DNS resolves to your machine's Tailscale IP
   
2. HTTPS request hits Caddy (listening on :443)
   └─ Caddy checks Caddyfile
   └─ Matches: ai.llm-server.your-tailnet.ts.net
   
3. Caddy reverse proxies to: localhost:3000
   └─ OpenWebUI container published port
   └─ PublishPort=127.0.0.1:3000:8080
   
4. Inside container: OpenWebUI listens on :8080
   └─ OpenWebUI needs LiteLLM
   └─ Connects to: http://litellm:4000 (via llm.network)
   
5. LiteLLM container receives request on :4000
   └─ LiteLLM needs database
   └─ Connects to: postgresql://llm-postgres:5432 (via llm.network)
   
6. Postgres container receives connection on :5432
   └─ Returns data
   
7. Response flows back through the stack
   └─ LiteLLM → OpenWebUI → Caddy → Tailscale → User
```

### Key Points:

- **External access:** Uses Tailscale + Caddy
- **Internal access:** Uses `llm.network` (containers talk by name)
- **No port conflicts:** Internal ports can overlap (multiple services on :8080)
- **Published ports:** Only for Caddy to access, not for external users

---

## Part 5: Service Folder Structure Example

### OpenWebUI Service (Complete)

**Folder:** `private_dot_config/containers/systemd/openwebui/`

```
openwebui/
├── openwebui.container.tmpl
├── openwebui.volume
├── openwebui.env.tmpl
└── README.md (optional)
```

#### File 1: `openwebui.container.tmpl`

```ini
# Generated by Chezmoi - DO NOT EDIT MANUALLY

[Unit]
Description=Open WebUI - AI Chat Interface
After=network-online.target llm.network.service
After=litellm.service llm-postgres.service llm-redis.service
Requires=llm.network.service
Wants=litellm.service llm-postgres.service llm-redis.service

[Container]
Image=ghcr.io/open-webui/open-webui:main
AutoUpdate=registry
ContainerName=openwebui

# Network - use shared llm.network
Network=llm

# Published port for Caddy to access
PublishPort=127.0.0.1:{{ .published_ports.openwebui }}:{{ .ports.openwebui }}

# Volume
Volume=openwebui.volume:/app/backend/data:Z

# Environment from service-specific config file
EnvironmentFile=%h/.config/containers/systemd/openwebui/openwebui.env

# Health check
HealthCmd="wget --no-verbose --tries=1 --spider http://localhost:{{ .ports.openwebui }}/health || exit 1"
HealthInterval=30s
HealthTimeout=5s
HealthRetries=3
HealthStartPeriod=10s

[Service]
Slice=llm.slice
TimeoutStartSec=900
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

#### File 2: `openwebui.volume`

```ini
[Volume]
VolumeName=openwebui-data
```

#### File 3: `openwebui.env.tmpl`

```bash
# Generated by Chezmoi - DO NOT EDIT MANUALLY
# OpenWebUI Environment Configuration

# Core Settings
PORT={{ .ports.openwebui }}
WEBUI_URL={{ .urls.openwebui }}
WEBUI_NAME=AI Assistant
ENV=prod
WEBUI_AUTH=true
ENABLE_SIGNUP={{ .service_config.openwebui.enable_signup }}
DEFAULT_USER_ROLE={{ .service_config.openwebui.default_user_role }}
WEBUI_SECRET_KEY={{ .services.openwebui.secret_key }}

# Database - uses service name from llm.network
DATABASE_URL=postgresql://{{ .database.postgres_user }}:{{ .database.postgres_password }}@llm-postgres:{{ .ports.postgres }}/openwebui

# Redis - uses service name from llm.network  
REDIS_URL=redis://llm-redis:{{ .ports.redis }}/2

# LiteLLM - uses service name from llm.network
OPENAI_API_BASE_URL=http://litellm:{{ .ports.litellm }}/v1
OPENAI_API_KEY={{ .api_keys.litellm_master }}

# Document Processing - uses service names
DOCLING_SERVER_URL=http://docling:{{ .ports.docling }}
TIKA_SERVER_URL=http://tika:{{ .ports.tika }}

# Search - uses service name
SEARXNG_QUERY_URL=http://searxng:{{ .ports.searxng }}/search?q=<query>
ENABLE_RAG_WEB_SEARCH=true

# Features
ENABLE_COMMUNITY_SHARING={{ .service_config.openwebui.enable_community_sharing }}
```

**Notice:**
- ✅ Uses service names: `litellm`, `llm-postgres`, `searxng`
- ✅ Not `localhost` - that would be wrong!
- ✅ Service names work because all containers are on `llm.network`

---

## Part 6: LiteLLM Service (Complete)

**Folder:** `private_dot_config/containers/systemd/litellm/`

```
litellm/
├── litellm.container.tmpl
└── litellm.yaml.tmpl
```

#### File 1: `litellm.container.tmpl`

```ini
# Generated by Chezmoi - DO NOT EDIT MANUALLY

[Unit]
Description=LiteLLM Proxy Service
After=network-online.target llm.network.service
After=llm-postgres.service llm-redis.service
Requires=llm.network.service
Wants=llm-postgres.service llm-redis.service

[Container]
Image=ghcr.io/berriai/litellm:main-stable
AutoUpdate=registry
ContainerName=litellm

# Network
Network=llm

# Published port
PublishPort=127.0.0.1:{{ .published_ports.litellm }}:{{ .ports.litellm }}

# Mount config file from same folder
Volume=%h/.config/containers/systemd/litellm/litellm.yaml:/app/config.yaml:ro,Z

# Environment variables
Environment=LITELLM_MASTER_KEY={{ .api_keys.litellm_master }}
Environment=DATABASE_URL=postgresql://{{ .database.postgres_user }}:{{ .database.postgres_password }}@llm-postgres:{{ .ports.postgres }}/litellm
Environment=REDIS_HOST=llm-redis
Environment=REDIS_PORT={{ .ports.redis }}

# API Keys
Environment=OPENAI_API_KEY={{ .api_keys.openai }}
Environment=ANTHROPIC_API_KEY={{ .api_keys.anthropic }}
Environment=GEMINI_API_KEY={{ .api_keys.gemini }}

# Execution
Exec=--config /app/config.yaml --port {{ .ports.litellm }} --num_workers 2

# Health check
HealthCmd="curl -f http://localhost:{{ .ports.litellm }}/health/readiness || exit 1"
HealthInterval=30s
HealthTimeout=10s
HealthRetries=3

[Service]
Slice=llm.slice
TimeoutStartSec=900
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

#### File 2: `litellm.yaml.tmpl`

```yaml
# Generated by Chezmoi - DO NOT EDIT MANUALLY

model_list:
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: {{ .api_keys.openai }}
  
  - model_name: claude-3-5-sonnet
    litellm_params:
      model: anthropic/claude-3-5-sonnet-latest
      api_key: {{ .api_keys.anthropic }}
  
  - model_name: gemini-2.0-flash
    litellm_params:
      model: gemini/gemini-2.0-flash-exp
      api_key: {{ .api_keys.gemini }}

litellm_settings:
  cache: true
  cache_params:
    type: redis
    host: llm-redis
    port: {{ .ports.redis }}

general_settings:
  database_url: "postgresql://{{ .database.postgres_user }}:{{ .database.postgres_password }}@llm-postgres:{{ .ports.postgres }}/litellm"
  master_key: {{ .api_keys.litellm_master }}
```

---

## Part 7: Postgres Service (Complete)

**Folder:** `private_dot_config/containers/systemd/llm-postgres/`

```
llm-postgres/
├── llm-postgres.container.tmpl
└── llm-postgres.volume
```

#### File 1: `llm-postgres.container.tmpl`

```ini
# Generated by Chezmoi - DO NOT EDIT MANUALLY

[Unit]
Description=Shared PostgreSQL database for LLM services
After=network-online.target llm.network.service
Requires=llm.network.service

[Container]
Image=docker.io/pgvector/pgvector:pg16
AutoUpdate=registry
ContainerName=llm-postgres

# Network - NO published port, only internal access
Network=llm

# Environment
Environment=POSTGRES_USER={{ .database.postgres_user }}
Environment=POSTGRES_PASSWORD={{ .database.postgres_password }}

# Volume
Volume=llm-postgres.volume:/var/lib/postgresql/data:Z

# PostgreSQL config
Exec=-c shared_preload_libraries={{ .service_config.postgres.shared_preload_libraries }} -c max_connections={{ .service_config.postgres.max_connections }}

# Health check
HealthCmd="pg_isready -U {{ .database.postgres_user }}"
HealthInterval=30s
HealthTimeout=5s
HealthRetries=5

[Service]
Slice=llm.slice
TimeoutStartSec=900
Restart=on-failure
RestartSec=10

# Create databases
{{- range $db := .database.postgres_databases }}
ExecStartPost=/bin/bash -c 'sleep 5 && podman exec llm-postgres psql -U {{ $.database.postgres_user }} -tc "SELECT 1 FROM pg_database WHERE datname = '"'"'{{ $db }}'"'"'" | grep -q 1 || podman exec llm-postgres psql -U {{ $.database.postgres_user }} -c "CREATE DATABASE {{ $db }};"'
{{- end }}

[Install]
WantedBy=default.target
```

#### File 2: `llm-postgres.volume`

```ini
[Volume]
VolumeName=llm-postgres-data
```

**Notice:** NO `PublishPort` - Postgres is internal only!

---

## Part 8: Updated .chezmoi.yaml.tmpl (Network-aware)

```yaml
data:
  # Network configuration
  network:
    name: "llm"
    subnet: "10.89.0.0/24"
    gateway: "10.89.0.1"
  
  # Internal container ports (what they listen on INSIDE)
  ports:
    postgres: 5432
    redis: 6379
    litellm: 4000
    openwebui: 8080
    searxng: 8080
    docling: 5001
    tika: 9998
    mcp: 8000
  
  # Published ports (host:container mapping for Caddy)
  published_ports:
    openwebui: 3000      # Host 3000 → Container 8080
    litellm: 4000        # Host 4000 → Container 4000
    searxng: 8888        # Host 8888 → Container 8080
    docling: 5001        # Host 5001 → Container 5001
    redis_ui: 8001       # Host 8001 → Container 8001
    # Note: postgres, tika, mcp - NO published ports (internal only)
  
  # External URLs (via Tailscale + Caddy)
  urls:
    cockpit: "https://{{ .tailscale.hostname }}.{{ .tailscale.tailnet }}"
    openwebui: "https://ai.{{ .tailscale.hostname }}.{{ .tailscale.tailnet }}"
    litellm: "https://litellm.{{ .tailscale.hostname }}.{{ .tailscale.tailnet }}"
    searxng: "https://search.{{ .tailscale.hostname }}.{{ .tailscale.tailnet }}"
```

---

## Part 9: Benefits of This Organization

### ✅ Clear Structure
- Each service has its own folder
- Easy to find all related files
- Can add per-service documentation

### ✅ Proper Network Layers
- Tailscale: External access
- Caddy: Routing to services
- llm.network: Container communication

### ✅ Maintainable
- Add new service: Create new folder
- Update service: Edit only that folder
- Shared config: Top-level files

### ✅ Secure
- Internal services (postgres, tika) have NO published ports
- Only entry point is Caddy via Tailscale
- Container network is isolated

### ✅ Scalable
- Easy to add more services
- Easy to add more databases
- Easy to reorganize

---

## Part 10: Quick Reference

### Network Troubleshooting:

```bash
# Check if llm.network exists
podman network ls | grep llm

# Inspect network
podman network inspect llm

# See which containers are on the network
podman network inspect llm | jq '.[].Containers'

# Test container-to-container communication
podman exec openwebui ping llm-postgres
podman exec openwebui curl http://litellm:4000/health
```

### Desktop Files Reference URLs:

```desktop
# openwebui.desktop.tmpl
Exec=google-chrome-stable --app={{ .urls.openwebui }}

# NOT localhost:3000 - use the Tailscale URL!
```

### Sway Keybinds Reference URLs:

```sway
# sway/config.tmpl
bindsym $mod+Shift+o exec google-chrome-stable --app={{ .urls.openwebui }}

# NOT localhost:3000 - use the Tailscale URL!
```

---

## Summary: The Three Networks

| Network | Purpose | Example | Access |
|---------|---------|---------|--------|
| **Tailscale** | External access | `ai.llm-server.tailnet.ts.net` | From anywhere on tailnet |
| **Caddy** | Proxy layer | `localhost:3000` | Host → Container |
| **llm.network** | Container-to-container | `litellm:4000` | Container → Container |

**Remember:**
- Desktop files & Sway → Use Tailscale URLs ({{ .urls.* }})
- Caddy → Proxies to localhost published ports
- Containers → Talk to each other via service names on llm.network
- llm.network file → Top level (shared infrastructure)

🎯 **Result:** Clean organization, proper network separation, maintainable structure!

---

# Final Clean Folder Structure - Ready to Build

## Complete Chezmoi Structure

```
~/.local/share/chezmoi/
│
├─── 📋 MASTER CONFIGURATION ─────────────────────────────────
│
├── .chezmoi.yaml.tmpl              ⭐ Single source of truth
│   ├─ network: llm, 10.89.0.0/24
│   ├─ ports: Internal container ports
│   ├─ published_ports: Host published ports  
│   ├─ urls: Tailscale external URLs
│   └─ webapps: Desktop launcher definitions
│
├── encrypted_private_secrets.yaml  🔒 All secrets encrypted
│   ├─ api_keys: OpenAI, Anthropic, etc.
│   ├─ database: Passwords
│   ├─ services: Secret keys
│   └─ tailscale: Auth key
│
├── .chezmoiignore                  (optional)
│
├─── 🖥️ DESKTOP ENVIRONMENT ──────────────────────────────────
│
├── private_dot_local/
│   └── private_share/
│       └── private_applications/   → ~/.local/share/applications/
│           ├── cockpit.desktop.tmpl
│           ├── openwebui.desktop.tmpl
│           ├── litellm.desktop.tmpl
│           ├── searxng.desktop.tmpl
│           ├── nextcloud.desktop.tmpl
│           └── (one per webapp - templates, not auto-generated)
│
├── private_dot_config/
│   │
│   ├── sway/                       → ~/.config/sway/
│   │   └── config.tmpl             (keybinds reference {{ .urls.* }})
│   │
│   ├─── 🌐 EXTERNAL ACCESS ──────────────────────────────────
│   │
│   ├── caddy/                      → ~/.config/caddy/
│   │   └── Caddyfile.tmpl          ⭐ Reverse proxy config
│   │       ├─ Routes Tailscale URLs → localhost ports
│   │       └─ Each service gets subdomain
│   │
│   ├── cockpit/                    → ~/.config/cockpit/
│   │   └── cockpit.conf.tmpl       (dashboard config)
│   │
│   └─── 🐳 CONTAINER INFRASTRUCTURE ─────────────────────────
│       │
│       └── containers/
│           └── systemd/            → ~/.config/containers/systemd/
│               │
│               ├─── SHARED INFRASTRUCTURE (top level) ───────
│               │
│               ├── llm.network     ⭐ SHARED NETWORK (static)
│               │   └─ All containers connect here
│               │   └─ 10.89.0.0/24 subnet
│               │   └─ Service name DNS resolution
│               │
│               ├── llm.env.tmpl    (optional: shared env vars)
│               │
│               ├─── SERVICE FOLDERS (organized by service) ──
│               │
│               ├── openwebui/      ⭐ MAIN UI
│               │   ├── openwebui.container.tmpl
│               │   │   ├─ Network=llm
│               │   │   ├─ PublishPort=3000:8080 (for Caddy)
│               │   │   └─ Connects to: litellm, postgres, redis
│               │   ├── openwebui.volume
│               │   └── openwebui.env.tmpl
│               │       └─ Uses service names: litellm:4000
│               │
│               ├── litellm/        ⭐ LLM PROXY
│               │   ├── litellm.container.tmpl
│               │   │   ├─ Network=llm
│               │   │   ├─ PublishPort=4000:4000 (for Caddy)
│               │   │   └─ Connects to: postgres, redis
│               │   └── litellm.yaml.tmpl
│               │       └─ Database: llm-postgres:5432
│               │
│               ├── llm-postgres/   ⭐ DATABASE
│               │   ├── llm-postgres.container.tmpl
│               │   │   ├─ Network=llm
│               │   │   ├─ NO PublishPort (internal only)
│               │   │   └─ Creates: litellm, openwebui, mcp DBs
│               │   └── llm-postgres.volume
│               │
│               ├── llm-redis/      ⭐ CACHE
│               │   ├── llm-redis.container.tmpl
│               │   │   ├─ Network=llm
│               │   │   ├─ PublishPort=8001:8001 (UI only)
│               │   │   └─ NO PublishPort for :6379 (internal)
│               │   └── llm-redis.volume
│               │
│               ├── searxng/        ⭐ SEARCH
│               │   ├── searxng.container.tmpl
│               │   │   ├─ Network=llm
│               │   │   ├─ PublishPort=8888:8080 (for Caddy)
│               │   │   └─ Connects to: redis
│               │   ├── searxng.volume
│               │   └── searxng-settings.yml.tmpl
│               │       └─ Redis: llm-redis:6379
│               │
│               ├── docling/        ⭐ DOCS
│               │   └── docling.container.tmpl
│               │       ├─ Network=llm
│               │       └─ PublishPort=5001:5001 (for Caddy)
│               │
│               ├── tika/           ⭐ EXTRACTION
│               │   └── tika.container.tmpl
│               │       ├─ Network=llm
│               │       └─ NO PublishPort (internal only)
│               │
│               ├── mcp/            ⭐ TOOLS
│               │   ├── mcp.container.tmpl
│               │   │   ├─ Network=llm
│               │   │   ├─ NO PublishPort (internal only)
│               │   │   └─ Connects to: postgres
│               │   └── mcp-config.json.tmpl
│               │       └─ Database: llm-postgres:5432
│               │
│               └── user/           → ~/.config/containers/systemd/user/
│                   │
│                   ├── nextcloud/
│                   │   └── nextcloud.container.tmpl
│                   │       └─ PublishPort=8443:80 (for Caddy)
│                   │
│                   └── whisper/
│                       └── whisper-npu.container.tmpl
│                           └─ PublishPort=8009:5000 (for Caddy)
│
└─── 🔧 AUTOMATION SCRIPTS ────────────────────────────────────
    │
    └── run_once_after/
        ├── 01-setup-tailscale.sh.tmpl
        ├── 02-setup-cockpit.sh.tmpl
        └── 03-reload-systemd.sh.tmpl
```

---

## Network Architecture Summary

### Three Separate Networks:

```
┌────────────────────────────────────────────────────────────┐
│ 1. TAILSCALE NETWORK (External)                            │
│    • Purpose: Secure remote access                         │
│    • URLs: *.llm-server.your-tailnet.ts.net               │
│    • Used by: Desktop files, Sway keybinds, browsers       │
│    • Authentication: Tailscale                             │
└─────────────┬──────────────────────────────────────────────┘
              │
              ↓
┌────────────────────────────────────────────────────────────┐
│ 2. CADDY PROXY LAYER (Host)                               │
│    • Listens: :443 (HTTPS)                                │
│    • Routes: Tailscale URL → localhost published port     │
│    • Example: ai.llm-server.ts.net → localhost:3000       │
└─────────────┬──────────────────────────────────────────────┘
              │
              ↓
┌────────────────────────────────────────────────────────────┐
│ 3. LLM.NETWORK (Containers)                               │
│    • Subnet: 10.89.0.0/24                                  │
│    • DNS: Service name resolution                          │
│    • Example: openwebui → litellm:4000                    │
│    • Purpose: Container-to-container communication         │
└────────────────────────────────────────────────────────────┘
```

### Port Mapping Table:

| Service | Internal Port | Published Port | Caddy Access | Purpose |
|---------|--------------|----------------|--------------|---------|
| **openwebui** | 8080 | 3000 | ✅ localhost:3000 | Main UI |
| **litellm** | 4000 | 4000 | ✅ localhost:4000 | LLM API |
| **postgres** | 5432 | ❌ None | ❌ Internal only | Database |
| **redis** | 6379 | ❌ None | ❌ Internal only | Cache |
| **redis-ui** | 8001 | 8001 | ✅ localhost:8001 | Monitoring |
| **searxng** | 8080 | 8888 | ✅ localhost:8888 | Search |
| **docling** | 5001 | 5001 | ✅ localhost:5001 | Docs |
| **tika** | 9998 | ❌ None | ❌ Internal only | Extraction |
| **mcp** | 8000 | ❌ None | ❌ Internal only | Tools |

**Key:**
- **Internal Port:** What container listens on
- **Published Port:** Host port mapped to container (127.0.0.1 only)
- **Caddy Access:** Can Caddy proxy to this?
- **Internal only:** No published port, only accessible via llm.network

---

## Service Communication Examples

### Example 1: User Opens OpenWebUI

```
Browser: https://ai.llm-server.your-tailnet.ts.net
    ↓ (Tailscale VPN)
Caddy: Routes ai.llm-server... to localhost:3000
    ↓ (Published port)
OpenWebUI Container: Receives request on :8080
    ↓ (Needs LLM)
    Connects to: http://litellm:4000 (via llm.network)
    ↓ (Service name DNS)
LiteLLM Container: Receives request on :4000
```

### Example 2: LiteLLM Queries Database

```
LiteLLM: Needs to log API call
    ↓ (Connection string from config)
    Connects to: postgresql://llm-postgres:5432/litellm
    ↓ (via llm.network service name)
Postgres Container: Receives connection on :5432
    ↓ (No published port needed!)
    Returns data over llm.network
```

### Example 3: OpenWebUI Uses Search

```
OpenWebUI: User asks to search web
    ↓ (Internal request)
    Connects to: http://searxng:8080/search
    ↓ (via llm.network)
SearXNG Container: Performs search
    ↓ (Needs cache)
    Connects to: redis://llm-redis:6379
    ↓ (via llm.network)
Redis Container: Returns cached results
```

**Notice:** All internal communication uses service names, no localhost!

---

## Configuration Flow

### How a URL Appears Everywhere:

```yaml
# 1. Define ONCE in .chezmoi.yaml.tmpl
data:
  tailscale:
    hostname: "llm-server"
    tailnet: "your-tailnet.ts.net"
  
  urls:
    openwebui: "https://ai.{{ .tailscale.hostname }}.{{ .tailscale.tailnet }}"
```

```desktop
# 2. Desktop file references it
# openwebui.desktop.tmpl
Exec=google-chrome-stable --app={{ .urls.openwebui }}
```

```sway
# 3. Sway config references it
# sway/config.tmpl
bindsym $mod+Shift+o exec google-chrome-stable --app={{ .urls.openwebui }}
```

```ini
# 4. Container env references it
# openwebui/openwebui.env.tmpl
WEBUI_URL={{ .urls.openwebui }}
```

```caddyfile
# 5. Caddy routes it
# Caddyfile.tmpl
ai.{{ .tailscale.hostname }}.{{ .tailscale.tailnet }}:443 {
    reverse_proxy localhost:{{ .published_ports.openwebui }}
}
```

**Result:** Change subdomain once → updates in 5 places automatically!

---

## Build Order (Sequential)

### Phase 1: Foundation (Week 1)
```bash
# Files to create:
1. .chezmoi.yaml.tmpl
2. encrypted_private_secrets.yaml
3. Caddyfile.tmpl
4. cockpit.conf.tmpl
5. Desktop files (5-8 .desktop.tmpl files)

# Test:
chezmoi apply -v
```

### Phase 2: Network & Shared (Week 1)
```bash
# Files to create:
6. llm.network (top level)
7. llm.env.tmpl (optional)

# Test:
podman network create llm --subnet 10.89.0.0/24
```

### Phase 3: Databases (Week 1-2)
```bash
# Folders to create:
8. llm-postgres/ folder + 2 files
9. llm-redis/ folder + 2 files

# Test:
systemctl --user start llm-postgres llm-redis
```

### Phase 4: Core Services (Week 2)
```bash
# Folders to create:
10. litellm/ folder + 2 files
11. openwebui/ folder + 3 files

# Test:
systemctl --user start litellm openwebui
```

### Phase 5: Supporting Services (Week 2-3)
```bash
# Folders to create:
12. searxng/ folder + 3 files
13. docling/ folder + 1 file
14. tika/ folder + 1 file
15. mcp/ folder + 2 files

# Test:
systemctl --user start searxng docling tika mcp
```

### Phase 6: User Services (Week 3)
```bash
# Folders to create:
16. user/nextcloud/ folder + 1 file
17. user/whisper/ folder + 1 file

# Test:
systemctl --user start nextcloud whisper
```

---

## Quick Commands

### Apply All Changes:
```bash
chezmoi apply -v
systemctl --user daemon-reload
```

### Test Network:
```bash
# Check network exists
podman network ls | grep llm

# Test container communication
podman exec openwebui ping litellm
podman exec openwebui curl http://litellm:4000/health
```

### Test External Access:
```bash
# From browser (anywhere on Tailscale):
https://ai.llm-server.your-tailnet.ts.net
```

### Debug:
```bash
# See generated file before applying
chezmoi cat ~/.config/containers/systemd/openwebui/openwebui.container

# See all configuration data
chezmoi data | jq .
```

---

## Key Takeaways

1. ✅ **Each service = one folder**
   - Clear organization
   - Easy to maintain
   - Can add per-service docs

2. ✅ **llm.network at top level**
   - Shared infrastructure
   - All services use it
   - Not specific to any service

3. ✅ **Three network layers**
   - Tailscale: External access
   - Caddy: Routing proxy
   - llm.network: Container communication

4. ✅ **Desktop files as templates**
   - Not auto-generated
   - Reference {{ .urls.* }}
   - Always point to correct URL

5. ✅ **Service names for internal communication**
   - Use `litellm:4000`, not `localhost:4000`
   - Works because of llm.network
   - Containers find each other by name

6. ✅ **Published ports only when needed**
   - For Caddy to access: Yes
   - For internal only: No
   - Reduces attack surface

---

🎯 **This structure is production-ready, maintainable, and scales well!**
