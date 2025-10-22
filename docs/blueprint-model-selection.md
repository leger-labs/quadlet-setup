# Blueprint.json Model Selection Guide

## Overview

The `blueprint.json` file is your **single source of truth** for configuring your Leger AI stack. For models, you only specify **model IDs** — everything else is fetched from the model-store.

## Basic Structure

```json
{
  "models": {
    "cloud": ["model-id-1", "model-id-2"],
    "local": ["model-id-3", "model-id-4"]
  }
}
```

### How It Works

1. **You specify IDs** in blueprint.json
2. **Render engine fetches** full definitions from `leger-run/model-store` on GitHub
3. **Generates configs** (litellm.yaml, llama-swap config.yml) with complete metadata
4. **Chezmoi applies** the rendered configs to your system

## Model Selection Examples

### Example 1: Cloud-Only Setup

**Use Case:** You have API keys and want cloud models only.

```json
{
  "models": {
    "cloud": [
      "gpt-5-mini",           // Fast, cost-efficient
      "claude-sonnet-4-5",    // Hybrid reasoning
      "gemini-2.5-flash"      // Long context (1M tokens)
    ],
    "local": []               // No local models
  }
}
```

**Result:**
- LiteLLM exposes 3 cloud models via API
- No llama-swap container needed
- Low memory footprint

### Example 2: Local-Only Setup

**Use Case:** Air-gapped system or no cloud API budget.

```json
{
  "models": {
    "cloud": [],              // No cloud models
    "local": [
      "qwen3-0.6b",           // Ultra-fast (1GB RAM)
      "qwen3-4b",             // Balanced (3GB RAM)
      "gpt-oss-20b",          // Heavy (16GB RAM)
      "qwen3-embedding-8b"    // Embeddings for RAG
    ]
  }
}
```

**Result:**
- llama-swap manages local models
- Task models (0.6B, 4B) always loaded
- Heavy model (20B) auto-swaps on demand
- No API keys needed

### Example 3: Hybrid Setup (Recommended)

**Use Case:** Best of both worlds — cloud for frontier, local for cost control.

```json
{
  "models": {
    "cloud": [
      "gpt-5",                // Frontier reasoning
      "claude-sonnet-4-5",    // Agentic workflows
      "gemini-2.5-pro"        // 2M context analysis
    ],
    "local": [
      "qwen3-0.6b",           // Title generation (instant)
      "qwen3-4b",             // Tag generation (instant)
      "gpt-oss-20b",          // General tasks (free)
      "qwen3-embedding-8b"    // RAG embeddings (free)
    ]
  }
}
```

**Result:**
- Cloud for hard problems (reasoning, long context)
- Local for routine tasks (titles, tags, embeddings)
- Cost-optimized workflow

### Example 4: Minimal Budget Setup

**Use Case:** Free tier models only.

```json
{
  "models": {
    "cloud": [
      "grok-4-fast",          // FREE (X.AI promotion)
      "deepseek-chat-v3.1"    // FREE (OpenRouter)
    ],
    "local": [
      "qwen3-4b",             // 3GB RAM
      "qwen3-embedding-8b"    // 9GB RAM
    ]
  }
}
```

**Result:**
- Total RAM: ~12GB
- Zero cloud API costs
- Good for experimentation

### Example 5: Maximum Capability Setup

**Use Case:** You have 128GB RAM and unlimited cloud budget.

```json
{
  "models": {
    "cloud": [
      "gpt-5-pro",            // Premium reasoning
      "claude-opus-4-1",      // 7-hour memory
      "gemini-2.5-pro"        // 2M context
    ],
    "local": [
      "qwen3-0.6b",           // Task (1GB)
      "qwen3-4b",             // Task (3GB)
      "qwen3-14b",            // Task (10GB)
      "gpt-oss-120b",         // Heavy (80GB)
      "qwen3-embedding-8b"    // Embeddings (9GB)
    ]
  }
}
```

**Result:**
- Total RAM: ~103GB
- Premium cloud models
- All capability tiers covered

## Model Selection Strategies

### Strategy 1: Capability Tiers

Organize by capability level:

```json
{
  "models": {
    "cloud": [
      "gpt-5-nano",           // ⚡ Fast tier
      "gpt-5-mini",           // 🔄 Balanced tier
      "gpt-5"                 // 🧠 Reasoning tier
    ],
    "local": [
      "qwen3-0.6b",           // ⚡ Task tier
      "qwen3-4b",             // 🔄 Balanced tier
      "gpt-oss-20b"           // 🧠 Heavy tier
    ]
  }
}
```

**Use fast for:** Titles, summaries, classification
**Use balanced for:** Chat, Q&A, simple code
**Use reasoning for:** Complex problems, research

### Strategy 2: Use Case Specific

Organize by primary use case:

```json
{
  "models": {
    "cloud": [
      "claude-sonnet-4-5",    // 💻 Code generation
      "gemini-2.5-flash",     // 📚 Document analysis
      "gpt-5"                 // 🤔 Reasoning
    ],
    "local": [
      "qwen3-0.6b",           // 🏷️ Metadata tasks
      "qwen3-coder-30b",      // 💻 Code review
      "qwen3-embedding-8b"    // 🔍 RAG embeddings
    ]
  }
}
```

### Strategy 3: Cost-Optimized

Minimize API costs:

```json
{
  "models": {
    "cloud": [
      "gpt-5-nano",           // $0.05/M (ultra-cheap)
      "gemini-2.5-flash"      // $0.30/M (cheap + 1M context)
    ],
    "local": [
      "qwen3-4b",             // Free (always loaded)
      "gpt-oss-20b",          // Free (auto-swap)
      "qwen3-embedding-8b"    // Free (embeddings)
    ]
  }
}
```

**Cost Estimate:**
- ~$5/month for moderate cloud usage
- All local inference free

## How Model IDs Are Resolved

### Resolution Flow

```
1. User edits blueprint.json
   └─> { "cloud": ["gpt-5"], "local": ["qwen3-4b"] }

2. Render engine (Cloudflare Worker) fetches model definitions
   └─> GET https://raw.githubusercontent.com/leger-run/model-store/main/cloud/gpt-5.json
   └─> GET https://raw.githubusercontent.com/leger-run/model-store/main/local/qwen3-4b.json

3. Render engine generates litellm.yaml
   └─> Includes full litellm_model_name, API endpoints, context limits

4. Render engine generates llama-swap config.yml
   └─> Includes model_uri, quantization, RAM requirements, group

5. Chezmoi applies rendered configs
   └─> ~/.config/containers/systemd/litellm/litellm.yaml
   └─> ~/.config/containers/systemd/llama-swap/config.yml

6. Services restart and pick up new models
   └─> systemctl --user restart litellm llama-swap
```

### What Gets Resolved

**For Cloud Models:**
```json
// You specify:
"gpt-5"

// Render engine fetches and resolves to:
{
  "model_name": "gpt-5",
  "litellm_params": {
    "model": "openai/gpt-5-2025-08-07",
    "api_key": "os.environ/OPENAI_API_KEY",
    "max_tokens": 400000,
    "stream": true
  }
}
```

**For Local Models:**
```json
// You specify:
"qwen3-4b"

// Render engine fetches and resolves to:
{
  "name": "qwen3-4b",
  "model_uri": "huggingface://Qwen/Qwen3-4B-GGUF/qwen3-4b-q4_k_m.gguf",
  "ctx_size": 8192,
  "ttl": 0,
  "group": "task"
}
```

## Adding Custom Models

### Option 1: Power User Override

Add a model that's not in the catalog:

```json
{
  "models": {
    "cloud": [
      "gpt-5",
      {
        "id": "my-custom-model",
        "provider": "openrouter",
        "litellm_model_name": "openrouter/custom/model",
        "context_window": 128000,
        "requires_api_key": "OPENROUTER_API_KEY"
      }
    ]
  }
}
```

Render engine will:
1. Fetch `gpt-5` from model-store
2. Use inline definition for `my-custom-model`

### Option 2: Contribute to Model Store

Better approach for reusability:

1. Fork `leger-run/model-store`
2. Add `cloud/my-custom-model.json`
3. Submit PR with justification
4. Once merged, use: `"cloud": ["my-custom-model"]`

## Model Configuration Overrides

Override specific parameters:

```json
{
  "models": {
    "cloud": [
      "gpt-5"
    ],
    "local": [
      "qwen3-4b"
    ]
  },

  "model_overrides": {
    "gpt-5": {
      "temperature": 0.7,
      "top_p": 0.9
    },
    "qwen3-4b": {
      "ctx_size": 16384,    // Increase from default 8192
      "ttl": 600            // Override: unload after 10 min
    }
  }
}
```

## Validation

### Schema Validation

The render engine validates:
- ✅ All model IDs exist in model-store
- ✅ Required API keys are configured
- ✅ RAM requirements fit your system
- ✅ No conflicts (e.g., duplicate model names)

### Error Examples

**Unknown Model ID:**
```json
{
  "models": {
    "cloud": ["gpt-6"]  // ❌ Doesn't exist
  }
}
```
**Error:** `Model 'gpt-6' not found in model-store. Available: gpt-5, gpt-5-mini, ...`

**Missing API Key:**
```json
{
  "models": {
    "cloud": ["gpt-5"]
  },
  "secrets": {
    "api_keys": {}  // ❌ Missing OPENAI_API_KEY
  }
}
```
**Error:** `Model 'gpt-5' requires OPENAI_API_KEY but it's not configured`

**Insufficient RAM:**
```json
{
  "models": {
    "local": ["qwen3-235b"]  // Requires 97GB
  }
}
```
**Warning:** `Model 'qwen3-235b' requires 97GB RAM. Your system has 64GB. Consider smaller model.`

## Best Practices

### 1. Start Small, Scale Up

```json
// Week 1: Test with minimal setup
{
  "models": {
    "cloud": ["gpt-5-mini"],
    "local": ["qwen3-4b"]
  }
}

// Week 2: Add more after testing
{
  "models": {
    "cloud": ["gpt-5-mini", "claude-sonnet-4-5"],
    "local": ["qwen3-4b", "gpt-oss-20b", "qwen3-embedding-8b"]
  }
}
```

### 2. Match Models to Hardware

```
16GB RAM:
  local: ["qwen3-0.6b", "qwen3-4b", "qwen3-embedding-8b"]
  Total: ~13GB

64GB RAM:
  local: ["qwen3-4b", "qwen3-14b", "gpt-oss-20b", "qwen3-embedding-8b"]
  Total: ~38GB

128GB RAM:
  local: ["qwen3-4b", "gpt-oss-120b", "qwen3-coder-30b", "qwen3-embedding-8b"]
  Total: ~102GB
```

### 3. Enable Models as Needed

Most models in model-store are `"enabled": false` by default. Enable them in blueprint.json when you need them:

```json
{
  "models": {
    "cloud": [
      "gpt-5-mini",           // Enabled by default
      "gpt-5-pro"             // Disabled by default - enable when needed
    ]
  }
}
```

### 4. Use Task Models for Automation

OpenWebUI can auto-assign task models:

```json
{
  "models": {
    "local": [
      "qwen3-0.6b",           // Auto: title generation
      "qwen3-4b"              // Auto: tag generation, queries
    ]
  },

  "openwebui": {
    "task_models": {
      "title_generation": "qwen3-0.6b",
      "tags_generation": "qwen3-4b",
      "query_generation": "qwen3-4b"
    }
  }
}
```

## Examples by Persona

### Researcher (Context Length Priority)

```json
{
  "models": {
    "cloud": [
      "gemini-2.5-pro",       // 2M tokens
      "claude-opus-4-1"       // 200K tokens + 7-hour memory
    ],
    "local": [
      "llama-4-scout-17b",    // 10M tokens (theoretical)
      "qwen3-embedding-8b"
    ]
  }
}
```

### Developer (Code Generation Priority)

```json
{
  "models": {
    "cloud": [
      "claude-sonnet-4-5",    // Best code generation
      "gpt-5"                 // Reasoning for architecture
    ],
    "local": [
      "qwen3-coder-30b",      // Code specialist
      "qwen3-4b"              // Quick tasks
    ]
  }
}
```

### Budget Conscious (Cost Priority)

```json
{
  "models": {
    "cloud": [
      "gpt-5-nano",           // $0.05/M
      "gemini-2.5-flash"      // $0.30/M
    ],
    "local": [
      "qwen3-4b",
      "gpt-oss-20b",
      "qwen3-embedding-8b"
    ]
  }
}
```

### Power User (Everything)

```json
{
  "models": {
    "cloud": [
      "gpt-5", "gpt-5-mini", "gpt-5-pro",
      "claude-sonnet-4-5", "claude-opus-4-1",
      "gemini-2.5-flash", "gemini-2.5-pro"
    ],
    "local": [
      "qwen3-0.6b", "qwen3-4b", "qwen3-14b",
      "gpt-oss-20b", "gpt-oss-120b",
      "qwen3-coder-30b", "qwen3-embedding-8b"
    ]
  }
}
```

## Migration from .chezmoi.yaml.tmpl

If you have models defined in `.chezmoi.yaml.tmpl`, migration is simple:

**Old (.chezmoi.yaml.tmpl):**
```yaml
litellm:
  models:
    - name: "gpt-5"
      provider: "openai"
      full_model_id: "gpt-5-2025-08-07"
      # ... 20 more fields
```

**New (blueprint.json):**
```json
{
  "models": {
    "cloud": ["gpt-5"]
  }
}
```

All the metadata moves to model-store. Blueprint only has IDs.

## Summary

**Simple Mental Model:**
1. ✅ Blueprint.json = **What models do I want?** (IDs only)
2. ✅ Model-store = **How do I configure them?** (metadata)
3. ✅ Render engine = **Connects the two** (fetches + generates configs)

**Three Steps to Add a Model:**
1. Check `njk/model-store/cloud/` or `local/` for available IDs
2. Add ID to `blueprint.json` → `models.cloud` or `models.local`
3. Done! Render engine handles the rest.

---

**See Also:**
- `blueprint.json.example` - Full blueprint example
- `njk/model-store/README.md` - Model catalog documentation
- Model Store Architecture doc - Full design rationale
