# Handoff: MCP Store Implementation

**Session Date:** 2025-10-22
**Branch:** `claude/model-store-architecture-011CUMt1a1afS4nVnViSs73u`
**Status:** Model Store Complete ✅ | MCP Store Design Complete ✅ | MCP Implementation Pending ⏳

---

## Session Summary

This session implemented the **Leger Model Store** architecture and designed the **MCP Store** structure. The model store is complete and functional; the MCP store design is documented but not yet implemented.

### What Was Accomplished

#### 1. Model Store (Complete ✅)

**Structure Created:**
```
njk/model-store/
├── cloud/               # 11 cloud API models
│   ├── gpt-5.json
│   ├── claude-sonnet-4-5.json
│   ├── gemini-2.5-flash.json
│   └── [8 more models]
├── local/               # 10 local GGUF models
│   ├── qwen3-0.6b.json
│   ├── qwen3-4b.json
│   ├── gpt-oss-20b.json
│   └── [7 more models]
├── schemas/
│   ├── cloud.schema.json    # Comprehensive validation
│   └── local.schema.json    # Comprehensive validation
├── assets/
│   └── README.md            # Placeholder for provider icons
└── README.md                # Curator guide
```

**Documentation Created:**
- `blueprint.json.example` - Basic model selection example
- `blueprint-full.json.example` - Full example with MCP config
- `docs/blueprint-model-selection.md` - 600+ line comprehensive guide
- `docs/blueprint-mcp-configuration.md` - MCP design document (draft)

**Key Features:**
- One JSON file per model (easy to add/update/deprecate)
- Rolling updates (no versioning)
- Rich metadata schemas (20+ fields for cloud, 25+ for local)
- Curator workflows documented (3-min add, 2-min update, 1-min deprecate)
- Quality criteria defined for model inclusion
- Deprecation strategy with replacement suggestions
- Community contribution guidelines

**Commits:**
1. `aebfa86` - feat(model-store): implement initial model catalog with comprehensive schemas
2. `549b242` - docs: add blueprint.json model selection guide and example

#### 2. MCP Store (Design Complete ✅, Implementation Pending ⏳)

**Design Pattern:**
- **Same pattern as model-store:** One file per MCP server, rolling updates, IDs in blueprint.json
- **Structure planned:**
  ```
  njk/mcp-store/
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

**Integration Points Identified:**
- OpenWebUI: `ENABLE_DIRECT_CONNECTIONS` + `TOOL_SERVER_CONNECTIONS` (JSON array)
- MCP Context Forge: `mcp-catalog.yml` (auto-registration)
- Existing infrastructure: `mcp-context-forge` already deployed

---

## Architecture Overview

### Core Principle: Orthogonal Separation

**Three Layers:**
1. **Infrastructure (Quadlets):** How services run (containers, networks, volumes)
2. **Models (model-store):** What LLMs are available (metadata, endpoints, capabilities)
3. **Tools (mcp-store):** What tools LLMs can use (commands, transports, capabilities)

**Each layer:**
- ✅ Maintained independently
- ✅ Rolling updates (no versions)
- ✅ Simple blueprint.json (IDs only)
- ✅ Metadata in separate store
- ✅ Render engine connects them

### Resolution Flow (Models - Already Working)

```
1. User: blueprint.json
   └─> { "models": { "cloud": ["gpt-5"], "local": ["qwen3-4b"] } }

2. Render Engine: Fetch definitions
   └─> GET model-store/cloud/gpt-5.json
   └─> GET model-store/local/qwen3-4b.json

3. Render Engine: Generate configs
   └─> litellm.yaml (with full API configs)
   └─> llama-swap config.yml (with model URIs)

4. Chezmoi: Apply configs
   └─> ~/.config/containers/systemd/litellm/litellm.yaml
   └─> ~/.config/containers/systemd/llama-swap/config.yml

5. Services: Restart
   └─> systemctl --user restart litellm llama-swap
```

### Resolution Flow (MCP - Needs Implementation)

```
1. User: blueprint.json
   └─> { "mcp_servers": { "enabled": ["filesystem", "github"] } }

2. Render Engine: Fetch definitions
   └─> GET mcp-store/servers/filesystem.json
   └─> GET mcp-store/servers/github.json

3. Render Engine: Generate configs
   └─> TOOL_SERVER_CONNECTIONS JSON (for OpenWebUI)
   └─> mcp-catalog.yml (for Context Forge)

4. Chezmoi: Apply configs
   └─> ~/.config/containers/systemd/openwebui/openwebui.env
   └─> ~/.config/mcp-context-forge/mcp-catalog.yml

5. Services: Restart
   └─> systemctl --user restart openwebui mcp-context-forge
```

---

## Current Codebase State

### Completed Files

**Model Store:**
- `njk/model-store/schemas/cloud.schema.json` - JSON schema for cloud models
- `njk/model-store/schemas/local.schema.json` - JSON schema for local models
- `njk/model-store/cloud/*.json` - 11 cloud model definitions
- `njk/model-store/local/*.json` - 10 local model definitions
- `njk/model-store/README.md` - Curator guide with workflows

**Documentation:**
- `blueprint.json.example` - Basic example
- `blueprint-full.json.example` - Full example with MCP
- `docs/blueprint-model-selection.md` - Model selection guide
- `docs/blueprint-mcp-configuration.md` - MCP design (draft)

**Existing Infrastructure (Already Deployed):**
- `njk/mcp-context-forge/` - MCP Context Forge quadlet
- `njk/mcp-context-forge/postgres/` - PostgreSQL for gateway
- `njk/mcp-context-forge/mcp-context-forge.container.njk` - Container def
- `njk/mcp-context-forge/mcp-context-forge-README.md` - Gateway docs
- `containers/systemd/_config/mcp-config.json` - Legacy MCP config

### Key Files to Understand

#### 1. Model Store Schema (Cloud)
**File:** `njk/model-store/schemas/cloud.schema.json`

**Required fields:**
- `id` - Unique identifier (e.g., "gpt-5")
- `name` - Display name
- `provider` - Cloud provider (openai, anthropic, gemini, etc.)
- `litellm_model_name` - Full LiteLLM identifier (provider/model-id)
- `context_window` - Max tokens
- `requires_api_key` - Env var name

**Optional fields:**
- `description`, `icon`, `capabilities`, `pricing`, `use_cases`, `features`, `performance`, `parameters`, `deprecated`, `replacement`, etc.

#### 2. Model Store Schema (Local)
**File:** `njk/model-store/schemas/local.schema.json`

**Required fields:**
- `id` - Unique identifier (e.g., "qwen3-4b")
- `name` - Display name
- `model_uri` - HuggingFace GGUF URI
- `quantization` - GGUF format (Q4_K_M, Q8_0, etc.)
- `ram_required_gb` - RAM needed
- `context_window` - Max tokens
- `group` - Model group (task, balanced, heavy, embeddings)

**Optional fields:**
- `description`, `family`, `capabilities`, `ctx_size`, `ttl`, `vulkan_driver`, `flash_attn`, etc.

#### 3. Blueprint Structure
**File:** `blueprint-full.json.example`

Shows complete blueprint structure:
- `metadata` - Project info
- `models.cloud` - Cloud model IDs array
- `models.local` - Local model IDs array
- `mcp_servers.enabled` - MCP server IDs array (DESIGN ONLY)
- `mcp_gateway` - Gateway config (DESIGN ONLY)
- `openwebui` - UI config with MCP integration (DESIGN ONLY)
- `features` - Feature flags
- `providers` - Provider selections
- `secrets` - API keys and secrets

#### 4. MCP Context Forge Infrastructure
**File:** `njk/mcp-context-forge/mcp-context-forge-README.md`

Comprehensive documentation for the gateway:
- Features: Federation, Auth, A2A, Multi-tenancy, Observability
- Configuration: Database, secrets, environment variables
- Server registration: UI, API, catalog methods
- Virtual servers: Bundle tools from multiple servers
- Troubleshooting: Common issues and solutions

#### 5. Legacy MCP Config
**File:** `containers/systemd/_config/mcp-config.json`

Current format (will be replaced):
```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/New_York"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://..."]
    }
  }
}
```

**Migration plan:** Move to njk/mcp-store/servers/*.json format

---

## Next Session Tasks: MCP Store Implementation

### Phase 1: Structure Setup (30 minutes)

**Task 1.1: Create MCP Store Directory**
```bash
mkdir -p njk/mcp-store/{servers,schemas}
```

**Task 1.2: Create JSON Schema**
Create `njk/mcp-store/schemas/mcp-server.schema.json`:

**Required fields:**
- `id` - Unique identifier (e.g., "filesystem", "github")
- `name` - Display name
- `description` - What the server does
- `provider` - Provider/maintainer
- `command` - Executable command
- `args` - Command arguments array
- `transport` - Transport type (stdio, sse, ws, http)
- `tools` - Array of tool identifiers

**Optional fields:**
- `capabilities`, `requires_auth`, `auth_env_var`, `category`, `tags`, `container_image`, `url`, `enabled`, `deprecated`, `replacement`

**Example schema structure:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://leger.run/schemas/mcp-store/server.schema.json",
  "title": "MCP Server Definition",
  "type": "object",
  "required": ["id", "name", "description", "provider", "transport"],
  "properties": {
    "id": { "type": "string", "pattern": "^[a-z0-9-]+$" },
    "name": { "type": "string" },
    "description": { "type": "string" },
    "provider": { "type": "string" },
    "command": { "type": "string" },
    "args": { "type": "array", "items": { "type": "string" } },
    "transport": { "enum": ["stdio", "sse", "ws", "http"] },
    "tools": { "type": "array", "items": { "type": "string" } },
    ...
  }
}
```

### Phase 2: Extract Existing Servers (1 hour)

**Task 2.1: Core Servers (Official MCP)**

Create these files in `njk/mcp-store/servers/`:

**time.json:**
```json
{
  "id": "time",
  "name": "Time Tools",
  "description": "Get current time in various timezones",
  "provider": "modelcontextprotocol",
  "command": "uvx",
  "args": ["mcp-server-time", "--local-timezone=America/New_York"],
  "transport": "stdio",
  "tools": ["get_current_time", "convert_timezone"],
  "capabilities": ["tools"],
  "requires_auth": false,
  "category": "utility",
  "tags": ["time", "timezone", "datetime"],
  "enabled": true
}
```

**filesystem.json:**
```json
{
  "id": "filesystem",
  "name": "Filesystem Tools",
  "description": "Read, write, and manage files and directories",
  "provider": "modelcontextprotocol",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
  "transport": "stdio",
  "tools": [
    "filesystem_read",
    "filesystem_write",
    "filesystem_list",
    "filesystem_delete",
    "filesystem_move",
    "filesystem_search"
  ],
  "capabilities": ["tools"],
  "requires_auth": false,
  "category": "system",
  "tags": ["filesystem", "files", "io", "storage"],
  "enabled": true
}
```

**postgres.json:**
```json
{
  "id": "postgres",
  "name": "PostgreSQL Tools",
  "description": "Query and manage PostgreSQL databases",
  "provider": "modelcontextprotocol",
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-postgres",
    "postgresql://llm_admin:llm-postgres-password@llm-postgres/mcp"
  ],
  "transport": "stdio",
  "tools": [
    "postgres_query",
    "postgres_list_tables",
    "postgres_describe_table",
    "postgres_execute"
  ],
  "capabilities": ["tools"],
  "requires_auth": true,
  "auth_type": "connection_string",
  "category": "database",
  "tags": ["postgres", "database", "sql"],
  "notes": "Connection string should be templated from secrets",
  "enabled": true
}
```

**git.json:**
```json
{
  "id": "git",
  "name": "Git Tools",
  "description": "Manage Git repositories and version control",
  "provider": "modelcontextprotocol",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-git"],
  "transport": "stdio",
  "tools": [
    "git_status",
    "git_diff",
    "git_log",
    "git_commit",
    "git_push",
    "git_pull",
    "git_branch",
    "git_checkout"
  ],
  "capabilities": ["tools"],
  "requires_auth": false,
  "category": "development",
  "tags": ["git", "vcs", "version-control"],
  "enabled": true
}
```

**Task 2.2: Integration Servers**

**github.json:**
```json
{
  "id": "github",
  "name": "GitHub Integration",
  "description": "Search repositories, create issues, manage pull requests",
  "provider": "github",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "transport": "stdio",
  "tools": [
    "github_search_repos",
    "github_search_code",
    "github_create_issue",
    "github_list_issues",
    "github_create_pr",
    "github_list_prs",
    "github_get_file"
  ],
  "capabilities": ["tools"],
  "requires_auth": true,
  "auth_env_var": "GITHUB_PAT",
  "category": "integration",
  "tags": ["github", "git", "code", "collaboration"],
  "enabled": true
}
```

**web-search.json:**
```json
{
  "id": "web-search",
  "name": "Web Search",
  "description": "Search the web using various search engines",
  "provider": "brave",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "transport": "stdio",
  "tools": [
    "web_search",
    "web_search_local"
  ],
  "capabilities": ["tools"],
  "requires_auth": true,
  "auth_env_var": "BRAVE_API_KEY",
  "category": "research",
  "tags": ["search", "web", "research"],
  "enabled": false,
  "notes": "Alternative to SearXNG for MCP-based search"
}
```

**Task 2.3: Productivity Servers (Optional - Add if needed)**

Create placeholders for:
- `email.json` - Email integration
- `calendar.json` - Calendar management
- `slack.json` - Slack messaging
- `todoist.json` - Task management
- `notion.json` - Notion workspace

Set `"enabled": false` for these initially.

### Phase 3: Create README (30 minutes)

**Task 3.1: Create njk/mcp-store/README.md**

Follow the structure of `njk/model-store/README.md`:
- Overview
- Directory structure
- Server schemas
- Curator workflows (add, update, deprecate)
- Quality criteria for server inclusion
- Integration points (OpenWebUI, Context Forge)
- Community contributions
- Current server inventory
- Examples by persona

**Key sections:**
1. **Adding a Server:** 3-minute workflow
2. **Server Registration Methods:**
   - Via Admin UI (Context Forge)
   - Via API
   - Via mcp-catalog.yml
3. **Virtual Servers:** Bundling tools
4. **Transport Types:** stdio, SSE, WebSocket, HTTP

### Phase 4: Render Engine Updates (Implementation - TBD)

**Note:** This is beyond the MCP store creation, but document the plan:

**Task 4.1: Fetch MCP Definitions**
Update render engine to:
- Read `blueprint.json` → `mcp_servers.enabled`
- Fetch each server JSON from `mcp-store/servers/`
- Validate against schema

**Task 4.2: Generate TOOL_SERVER_CONNECTIONS**
For OpenWebUI, generate:
```bash
ENABLE_DIRECT_CONNECTIONS=true
TOOL_SERVER_CONNECTIONS='[
  {"name": "filesystem", "url": "http://mcp-context-forge:4444/servers/filesystem/sse"},
  {"name": "github", "url": "http://mcp-context-forge:4444/servers/github/sse"}
]'
```

**Task 4.3: Generate mcp-catalog.yml**
For MCP Context Forge, generate:
```yaml
servers:
  - name: filesystem
    url: http://mcp-filesystem:8080/sse
    transport: sse
    description: "..."
    enabled: true

  - name: github
    url: http://mcp-github:8080/sse
    transport: sse
    description: "..."
    enabled: true
```

---

## Key Design Decisions

### 1. One File Per Server
**Why:** Easy to add, update, deprecate. Git-friendly. Clear ownership.

### 2. IDs Only in Blueprint
**Why:** Simple for users. Metadata centralized. Easy to update.

### 3. Rolling Updates (No Versions)
**Why:** Servers don't break like infrastructure. Adding a server doesn't affect others.

### 4. Gateway-Centric Architecture
**Why:** Federation, auth, observability. Single endpoint for OpenWebUI.

### 5. Separation from Model Store
**Why:** Models and tools are orthogonal concerns. Independent maintenance.

---

## Important Considerations

### 1. MCP Context Forge is Already Deployed
- **Location:** `njk/mcp-context-forge/`
- **Status:** Quadlet configured, PostgreSQL backend ready
- **Access:** Admin UI at `http://localhost:4444/admin`
- **Auth:** JWT-based, user management via UI

### 2. OpenWebUI Integration
- **Var:** `ENABLE_DIRECT_CONNECTIONS` (already supported)
- **Var:** `TOOL_SERVER_CONNECTIONS` (JSON array format)
- **URL Pattern:** `http://mcp-context-forge:4444/servers/{name}/sse`

### 3. Server Transports
- **stdio:** Process-based, command + args
- **SSE:** Server-sent events over HTTP
- **WebSocket:** Bidirectional streaming
- **HTTP:** RESTful API calls

### 4. Authentication Patterns
- **No auth:** time, filesystem (localhost only)
- **Env var:** github (GITHUB_PAT), web-search (BRAVE_API_KEY)
- **Connection string:** postgres (embedded in args)
- **Bearer token:** Custom servers via Context Forge

### 5. Virtual Servers
**Feature:** Bundle tools from multiple servers
**Example:**
```json
{
  "name": "dev-tools",
  "tools": ["filesystem_read", "git_status", "github_create_pr"]
}
```
**Benefit:** Single endpoint, curated tool set per workflow

---

## Testing Plan

### Phase 1: Manual Validation
1. Create MCP server JSON files
2. Validate against schema (use JSON schema validator)
3. Check all required fields present
4. Verify tool names match conventions

### Phase 2: Integration Test (Manual)
1. Manually add server to MCP Context Forge via Admin UI
2. Test connection from OpenWebUI
3. Verify tools appear in UI
4. Test tool execution

### Phase 3: Automated Generation (Future)
1. Update render engine to fetch MCP definitions
2. Generate TOOL_SERVER_CONNECTIONS
3. Generate mcp-catalog.yml
4. Apply via Chezmoi
5. Test end-to-end flow

---

## Success Criteria

### MCP Store Creation (This Session's Scope)
- [ ] `njk/mcp-store/` directory structure created
- [ ] JSON schema for MCP servers defined
- [ ] 5-10 core servers extracted to individual JSON files
- [ ] README.md with curator workflows created
- [ ] Documentation updated (blueprint-mcp-configuration.md)

### Full MCP Integration (Future Session)
- [ ] Render engine fetches MCP server definitions
- [ ] Generates TOOL_SERVER_CONNECTIONS for OpenWebUI
- [ ] Generates mcp-catalog.yml for Context Forge
- [ ] Nunjucks templates use MCP IDs (not hardcoded configs)
- [ ] End-to-end test: blueprint.json → working MCP tools

---

## References

### Documentation Created This Session
- `njk/model-store/README.md` - Model store curator guide
- `docs/blueprint-model-selection.md` - Model selection comprehensive guide
- `docs/blueprint-mcp-configuration.md` - MCP configuration design (draft)
- `blueprint.json.example` - Basic blueprint example
- `blueprint-full.json.example` - Full blueprint with MCP

### Existing Documentation
- `njk/mcp-context-forge/mcp-context-forge-README.md` - Gateway comprehensive docs
- `mcp/servers.md` - Server ideas and references
- `mcp/task-management.md` - Task management integration ideas

### External References
- **MCP Context Forge:** https://github.com/IBM/mcp-context-forge
- **MCP Specification:** https://spec.modelcontextprotocol.io/
- **Official MCP Servers:** https://github.com/modelcontextprotocol/servers
- **OpenWebUI MCP Docs:** https://docs.openwebui.com/features/mcp
- **Supercamp AI (Reference):** https://supercamp.ai/

---

## Repository State

### Branch
`claude/model-store-architecture-011CUMt1a1afS4nVnViSs73u`

### Recent Commits
```
549b242 docs: add blueprint.json model selection guide and example
aebfa86 feat(model-store): implement initial model catalog with comprehensive schemas
4f14d3f Merge pull request #13 (template reorganization)
```

### Working Tree
Clean - all changes committed and pushed.

### Files Added This Session (25 files total)
**Model Store:**
- 2 schemas (cloud, local)
- 11 cloud models
- 10 local models
- 2 READMEs

**Documentation:**
- blueprint.json.example
- blueprint-full.json.example
- docs/blueprint-model-selection.md
- docs/blueprint-mcp-configuration.md
- HANDOFF-MCP-IMPLEMENTATION.md (this file)

---

## Quick Start for Next Session

```bash
# 1. Check out branch
git checkout claude/model-store-architecture-011CUMt1a1afS4nVnViSs73u
git pull origin claude/model-store-architecture-011CUMt1a1afS4nVnViSs73u

# 2. Review existing model store
ls -R njk/model-store/

# 3. Read design documents
cat docs/blueprint-mcp-configuration.md
cat njk/model-store/README.md
cat blueprint-full.json.example

# 4. Create MCP store structure
mkdir -p njk/mcp-store/{servers,schemas}

# 5. Start with schema
# Create: njk/mcp-store/schemas/mcp-server.schema.json

# 6. Extract core servers
# Create: njk/mcp-store/servers/{time,filesystem,postgres,git,github}.json

# 7. Create README
# Create: njk/mcp-store/README.md

# 8. Commit and push
git add njk/mcp-store/
git commit -m "feat(mcp-store): implement MCP server catalog"
git push
```

---

## Questions for Next Session

1. **Transport preference:** Should default be stdio (process-based) or SSE (server-based)?
2. **Container images:** Should we define containerized MCP servers or stick to command-based?
3. **Virtual servers:** Should these be defined in blueprint.json or managed via Context Forge UI?
4. **Catalog format:** YAML or JSON for mcp-catalog file?
5. **Authentication:** How to template secrets (connection strings, API keys) in MCP server definitions?

---

## Final Notes

### Architecture Achievement
This session successfully separated **models** (what LLMs are available) from **infrastructure** (how services run). The next session will complete the trinity by separating **tools** (what LLMs can use) into the MCP store.

### Pattern Established
The model-store implementation serves as a perfect template for the mcp-store. Follow the same structure:
- One file per entity
- JSON schema for validation
- IDs in blueprint.json
- Metadata in store
- Render engine connects them
- Rolling updates (no versions)

### User Request Fulfilled
The user specifically requested:
1. ✅ Model selection in blueprint.json - DONE
2. ⏳ MCP configuration in blueprint.json - DESIGNED (implementation pending)

The MCP store will enable the same simple selection pattern:
```json
{
  "models": { "cloud": ["gpt-5"], "local": ["qwen3-4b"] },
  "mcp_servers": { "enabled": ["filesystem", "github"] }
}
```

Everything else is fetched from the respective stores.

---

**Handoff prepared by:** Claude Code (Session 2025-10-22)
**Next session goal:** Implement `njk/mcp-store/` with 5-10 core servers
**Estimated time:** 2-3 hours for complete MCP store setup

Good luck! 🚀
