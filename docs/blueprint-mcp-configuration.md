# Blueprint.json MCP Configuration (Draft)

## Overview

MCP (Model Context Protocol) servers provide tools and resources that LLMs can use to interact with external systems. This document outlines how MCP servers are configured in blueprint.json.

## Current Status

⚠️ **DRAFT - Implementation Pending**

This is a design draft. The MCP configuration system follows the same pattern as model selection but needs full implementation.

## Configuration Structure

### Simple Form (Just IDs)

```json
{
  "mcp_servers": {
    "enabled": [
      "time",
      "filesystem",
      "postgres",
      "git",
      "github"
    ]
  }
}
```

### Detailed Form (With Gateway Config)

```json
{
  "mcp_servers": {
    "enabled": [
      "time",
      "filesystem",
      "postgres",
      "git",
      "github",
      "web-search"
    ],
    "disabled": [
      "email",
      "calendar",
      "slack"
    ]
  },

  "mcp_gateway": {
    "enabled": true,
    "mode": "context-forge",
    "auth_required": true,
    "catalog_enabled": true,
    "a2a_enabled": true,
    "federation_enabled": true
  },

  "openwebui": {
    "direct_connections": true,
    "mcp_integration": {
      "enabled": true,
      "gateway_url": "http://mcp-context-forge:4444",
      "virtual_servers": [
        {
          "name": "dev-tools",
          "tools": ["filesystem_read", "filesystem_write", "git_status"]
        }
      ]
    }
  }
}
```

## How It Should Work (Design Intent)

### 1. MCP Server Definitions

Similar to model-store, create `njk/mcp-store/` with individual server definitions:

```
mcp-store/
├── servers/
│   ├── time.json
│   ├── filesystem.json
│   ├── postgres.json
│   ├── git.json
│   ├── github.json
│   └── [one file per server]
├── schemas/
│   └── mcp-server.schema.json
└── README.md
```

### 2. Server Definition Example

**mcp-store/servers/filesystem.json:**
```json
{
  "id": "filesystem",
  "name": "Filesystem Tools",
  "description": "Read and write files, list directories",
  "provider": "modelcontextprotocol",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
  "transport": "stdio",
  "tools": [
    "filesystem_read",
    "filesystem_write",
    "filesystem_list",
    "filesystem_delete"
  ],
  "capabilities": ["tools"],
  "container_image": null,
  "requires_auth": false,
  "category": "system",
  "tags": ["filesystem", "files", "io"],
  "enabled": true
}
```

**mcp-store/servers/github.json:**
```json
{
  "id": "github",
  "name": "GitHub Integration",
  "description": "Search repositories, create issues, manage PRs",
  "provider": "github",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "transport": "stdio",
  "tools": [
    "github_search_repos",
    "github_create_issue",
    "github_list_prs",
    "github_create_pr"
  ],
  "capabilities": ["tools"],
  "requires_auth": true,
  "auth_env_var": "GITHUB_PAT",
  "category": "productivity",
  "tags": ["github", "git", "vcs"],
  "enabled": true
}
```

### 3. Resolution Flow (Design)

```
1. User edits blueprint.json
   └─> { "mcp_servers": { "enabled": ["filesystem", "github"] } }

2. Render engine fetches server definitions
   └─> GET mcp-store/servers/filesystem.json
   └─> GET mcp-store/servers/github.json

3. Generates TOOL_SERVER_CONNECTIONS for OpenWebUI
   └─> JSON array for TOOL_SERVER_CONNECTIONS env var

4. Generates mcp-catalog.yml for MCP Context Forge
   └─> YAML catalog file with all enabled servers

5. Chezmoi applies configs
   └─> ~/.config/containers/systemd/openwebui/openwebui.env
   └─> ~/.config/mcp-context-forge/mcp-catalog.yml

6. Services restart and pick up new MCP servers
   └─> systemctl --user restart openwebui mcp-context-forge
```

### 4. Generated Outputs (Design)

**For OpenWebUI (openwebui.env):**
```bash
ENABLE_DIRECT_CONNECTIONS=true
TOOL_SERVER_CONNECTIONS='[
  {
    "name": "filesystem",
    "url": "http://mcp-context-forge:4444/servers/filesystem/sse",
    "api_key": ""
  },
  {
    "name": "github",
    "url": "http://mcp-context-forge:4444/servers/github/sse",
    "api_key": ""
  }
]'
```

**For MCP Context Forge (mcp-catalog.yml):**
```yaml
servers:
  - name: filesystem
    url: http://mcp-filesystem:8080/sse
    transport: sse
    description: Read and write files, list directories
    tags: [filesystem, files, io]
    enabled: true

  - name: github
    url: http://mcp-github:8080/sse
    transport: sse
    description: Search repositories, create issues, manage PRs
    tags: [github, git, vcs]
    enabled: true
    auth_type: bearer
```

## Available MCP Servers (Planned)

### Core Tools (Official MCP Servers)
- **time** - Current time and timezone tools
- **filesystem** - File operations (read, write, list)
- **postgres** - PostgreSQL database queries
- **sqlite** - SQLite database queries
- **git** - Git repository operations

### Integrations (Third-party)
- **github** - GitHub API integration
- **gitlab** - GitLab API integration
- **web-search** - Web search capabilities
- **email** - Email reading and sending
- **calendar** - Calendar events (Google/Outlook)
- **slack** - Slack messaging
- **todoist** - Task management
- **notion** - Notion workspace

### Development Tools
- **docker** - Docker container management
- **kubernetes** - K8s cluster management
- **aws** - AWS service management
- **terraform** - Infrastructure as code

## MCP Gateway Configuration

### Context Forge Mode (Default)

Uses IBM MCP Context Forge for enterprise features:
- Federation of multiple MCP servers
- Authentication and authorization
- Admin UI for server management
- Virtual servers (bundle tools)
- A2A (agent-to-agent) support

```json
{
  "mcp_gateway": {
    "enabled": true,
    "mode": "context-forge",
    "auth_required": true,
    "catalog_enabled": true,
    "a2a_enabled": true
  }
}
```

### Direct Mode (Simple)

OpenWebUI connects directly to MCP servers (no gateway):

```json
{
  "mcp_gateway": {
    "enabled": false,
    "mode": "direct"
  },
  "openwebui": {
    "direct_connections": true
  }
}
```

Each MCP server runs as a separate container, OpenWebUI connects to each via stdio/SSE.

## Virtual Servers (Context Forge Feature)

Bundle tools from multiple servers into custom endpoints:

```json
{
  "openwebui": {
    "mcp_integration": {
      "virtual_servers": [
        {
          "name": "dev-tools",
          "description": "Development workflow tools",
          "tools": [
            "filesystem_read",
            "filesystem_write",
            "git_status",
            "git_commit",
            "github_create_pr"
          ]
        },
        {
          "name": "research-tools",
          "description": "Research and analysis",
          "tools": [
            "web_search",
            "github_search_repos",
            "postgres_query"
          ]
        }
      ]
    }
  }
}
```

## Configuration Strategies

### Strategy 1: Minimal Setup

Essential tools only:

```json
{
  "mcp_servers": {
    "enabled": ["time", "filesystem"]
  }
}
```

**Use case:** Basic functionality, low resource usage

### Strategy 2: Developer Setup

Git/GitHub workflow:

```json
{
  "mcp_servers": {
    "enabled": [
      "time",
      "filesystem",
      "git",
      "github",
      "postgres"
    ]
  }
}
```

**Use case:** Software development, code management

### Strategy 3: Research Setup

Web search and data tools:

```json
{
  "mcp_servers": {
    "enabled": [
      "time",
      "filesystem",
      "web-search",
      "postgres",
      "sqlite"
    ]
  }
}
```

**Use case:** Research, data analysis

### Strategy 4: Productivity Setup

Task and communication tools:

```json
{
  "mcp_servers": {
    "enabled": [
      "time",
      "filesystem",
      "email",
      "calendar",
      "todoist",
      "notion",
      "slack"
    ]
  }
}
```

**Use case:** Personal productivity, team collaboration

## Implementation Status

### ✅ Already Implemented
- MCP Context Forge quadlet configuration
- PostgreSQL backend for gateway
- Admin UI for server registration
- Caddy reverse proxy for external access

### ⏳ Needs Implementation
- [ ] Create `njk/mcp-store/` directory structure
- [ ] Define JSON schema for MCP server definitions
- [ ] Extract common MCP servers to individual JSON files
- [ ] Update render engine to fetch MCP definitions
- [ ] Generate `TOOL_SERVER_CONNECTIONS` for OpenWebUI
- [ ] Generate `mcp-catalog.yml` for Context Forge
- [ ] Update Nunjucks templates to use MCP IDs
- [ ] Add MCP server validation
- [ ] Document MCP server contribution process
- [ ] Create MCP server examples by persona

## References

- **MCP Context Forge:** https://github.com/IBM/mcp-context-forge
- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **OpenWebUI MCP:** https://docs.openwebui.com/features/mcp
- **Official MCP Servers:** https://github.com/modelcontextprotocol/servers

## Next Steps

1. **Create mcp-store structure** (similar to model-store)
2. **Define server schemas** (command, args, transport, tools)
3. **Extract existing servers** to individual JSON files
4. **Update render engine** to resolve MCP IDs
5. **Generate configs** (TOOL_SERVER_CONNECTIONS, mcp-catalog.yml)
6. **Test integration** with OpenWebUI and Context Forge

---

**Status:** Draft design document - awaiting implementation
**Last Updated:** 2025-10-22
