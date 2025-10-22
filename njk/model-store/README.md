# Leger Model Store

A curated, rolling-basis repository of LLM model definitions for the Leger AI platform.

## Overview

This model store contains metadata for **cloud API models** and **local GGUF models** that can be used with Leger's AI infrastructure. Models are defined individually in JSON files, making them easy to add, update, and deprecate.

**Key Principles:**
- **One file per model** - Easy to add, update, or deprecate
- **Rolling updates** - No versioning, always shows latest
- **Orthogonal to quadlets** - Models are data, not infrastructure
- **Quality over quantity** - Curated representatives, not exhaustive lists

## Directory Structure

```
model-store/
├── cloud/                    # Cloud API models (OpenAI, Anthropic, etc.)
│   ├── gpt-5.json
│   ├── claude-sonnet-4-5.json
│   └── [one file per model]
├── local/                    # Local GGUF models (Qwen, Llama, etc.)
│   ├── qwen3-4b.json
│   ├── gpt-oss-20b.json
│   └── [one file per model]
├── schemas/                  # JSON schemas for validation
│   ├── cloud.schema.json
│   └── local.schema.json
├── assets/                   # Provider logos and icons
│   └── [provider icons - TODO]
└── README.md                 # This file
```

## Model Schemas

### Cloud Models (cloud.schema.json)

**Required Fields:**
- `id` - Unique identifier (e.g., "gpt-5", "claude-sonnet-4-5")
- `name` - Display name for UI
- `provider` - Cloud provider (openai, anthropic, gemini, etc.)
- `litellm_model_name` - Full LiteLLM identifier (provider/model-id)
- `context_window` - Maximum context window in tokens
- `requires_api_key` - Environment variable name for API key

**Optional Fields:**
- `description` - Textual description (can be empty)
- `icon` - Path to provider logo in assets/
- `capabilities` - Array of capabilities (chat, vision, reasoning, etc.)
- `pricing` - Cost per 1M tokens (input_per_1m, output_per_1m, tier)
- `max_output` - Maximum output tokens
- `use_cases` - Recommended use cases
- `release_date` - Model release date
- `notes` - Additional notes
- `features` - Key features
- `performance` - Performance metrics
- `parameters` - Configurable parameters
- `deprecated` - Boolean flag
- `replacement` - Model ID to use instead (if deprecated)
- `enabled` - Whether enabled by default in blueprints

### Local Models (local.schema.json)

**Required Fields:**
- `id` - Unique identifier (e.g., "qwen3-4b", "gpt-oss-20b")
- `name` - Display name for UI
- `model_uri` - HuggingFace GGUF URI (huggingface://repo/file.gguf)
- `quantization` - GGUF quantization format (Q4_K_M, Q8_0, etc.)
- `ram_required_gb` - RAM required in GB
- `context_window` - Maximum context window in tokens
- `group` - Model group (task, balanced, heavy, embeddings)

**Optional Fields:**
- `description` - Textual description (can be empty)
- `icon` - Path to family logo in assets/
- `family` - Model family (qwen, llama, mistral, etc.)
- `capabilities` - Array of capabilities (chat, code, embeddings, etc.)
- `ctx_size` - Practical context size for optimal performance
- `ttl` - Time to live in seconds (0 = never unload)
- `hf_repo`, `hf_file` - HuggingFace repository details
- `aliases` - Alternative names for the model
- `shortname` - Short identifier
- `embedding_dimension` - For embedding models only
- `vulkan_driver` - Preferred Vulkan driver (RADV, AMDVLK)
- `flash_attn` - Whether to use flash attention
- `batch_size` - Batch size for inference
- `deprecated` - Boolean flag
- `replacement` - Model ID to use instead (if deprecated)
- `enabled` - Whether enabled by default in blueprints
- `use_cases` - Recommended use cases
- `notes` - Additional notes
- `performance` - Performance metrics

## Curator Workflows

### Adding a New Model (3 minutes)

1. Create new JSON file in appropriate directory:
   - Cloud: `cloud/model-id.json`
   - Local: `local/model-id.json`

2. Fill in required fields, add optional fields as available

3. Validate against schema (CI will check automatically)

4. Commit with descriptive message:
   ```bash
   git add cloud/gpt-5-nano.json
   git commit -m "feat: add GPT-5 Nano model"
   git push
   ```

5. Model appears in gallery immediately

**Example - Adding Cloud Model:**
```json
{
  "id": "gpt-5-nano",
  "name": "GPT-5 Nano",
  "provider": "openai",
  "litellm_model_name": "openai/gpt-5-nano-2025-08-07",
  "context_window": 400000,
  "requires_api_key": "OPENAI_API_KEY",
  "description": "Fastest, most cost-efficient GPT-5",
  "pricing": {
    "input_per_1m": "$0.05",
    "output_per_1m": "$0.40",
    "tier": "budget"
  },
  "enabled": true
}
```

### Updating a Model (2 minutes)

1. Edit existing JSON file
2. Update fields (pricing, context_window, description, etc.)
3. Commit with descriptive message
4. Push

**Example - Update Pricing:**
```bash
# Edit cloud/gpt-5.json to update pricing
git add cloud/gpt-5.json
git commit -m "chore: update GPT-5 pricing"
git push
```

### Deprecating a Model (1 minute)

1. Edit existing JSON file
2. Set `"deprecated": true`
3. Set `"replacement": "better-model-id"`
4. Optionally add `"deprecation_reason"` and `"sunset_date"`
5. Commit and push

**Example:**
```json
{
  "id": "gpt-4o",
  "deprecated": true,
  "replacement": "gpt-5",
  "deprecation_reason": "Superseded by GPT-5 family",
  "sunset_date": "2026-01-01"
}
```

Gallery UI will show deprecation warning and suggest replacement. Existing deployments continue to work.

### Monthly Audit (15 minutes)

1. Check provider release notes:
   - OpenAI: https://platform.openai.com/docs/models
   - Anthropic: https://docs.anthropic.com/en/docs/models-overview
   - Google: https://ai.google.dev/models/gemini

2. Scan HuggingFace trending GGUF models:
   - https://huggingface.co/models?library=gguf&sort=trending

3. Add 1-3 new models if they meet quality criteria

4. Update pricing if providers changed rates

5. Deprecate models if providers sunset them

## Quality Criteria

### Cloud Models - All Required

1. ✅ Listed in LiteLLM documentation
2. ✅ Publicly available (not private beta)
3. ✅ Has published pricing
4. ✅ From established provider
5. ✅ API endpoint verified working

### Local Models - All Required

1. ✅ GGUF format on HuggingFace
2. ✅ Has published benchmarks (MMLU, HumanEval)
3. ✅ 1000+ downloads (community validated)
4. ✅ Multiple quantizations available
5. ✅ Fits in 1GB-128GB RAM range

### What Gets Rejected

- ❌ Preview/beta models
- ❌ Unverified fine-tunes
- ❌ Models without benchmarks
- ❌ Redundant variants (we have Qwen3-4B, don't need Qwen3-4B-v2)
- ❌ Models from sketchy sources

## Coverage Strategy

**Don't list everything - curate representatives.**

### Cloud Model Dimensions

- **Capability Tier:** Frontier (GPT-5) → Mid (GPT-5 Mini) → Budget (GPT-5 Nano)
- **Context Window:** Small (8K) → Large (200K) → Massive (1M+)
- **Specialization:** General chat, reasoning, vision, code

### Local Model Dimensions

- **Size Class:** Task (<2GB) → Balanced (4-8GB) → Heavy (12-24GB)
- **Use Case:** Chat, embedding, code, vision
- **Family:** Qwen, Llama, Mistral, Phi, Gemma, Granite

**Example:** Don't include every Qwen3 quantization. Include Q4_K_M as standard. Power users can manually add others to blueprint.json.

## Integration Points

### Gallery View (app.leger.run/models)

1. Fetches all files from `cloud/` and `local/` via GitHub API
2. Parses JSON for each model
3. Filters out deprecated models (or shows with warning)
4. Renders as cards with provider icon, description, capabilities
5. "Install" button adds model ID to user's blueprint.json

### Render Engine (Cloudflare Worker)

1. User saves blueprint.json with model IDs
2. Render engine fetches model definitions from GitHub
3. Resolves each ID to full metadata
4. Generates litellm.yaml with complete configurations
5. Generates llama-swap config.yml for local models

### User's blueprint.json

**Users only specify IDs:**
```json
{
  "models": {
    "cloud": ["gpt-5", "claude-sonnet-4-5"],
    "local": ["qwen3-4b", "qwen3-0.6b"]
  }
}
```

Everything else (pricing, context limits, API endpoints) fetched from model-store.

## Community Contributions

### How to Propose a Model

1. Fork the repository
2. Create new JSON file following schema
3. Fill in all required fields
4. Submit PR with justification:
   - Why this model should be included
   - Link to benchmarks or LiteLLM docs
   - Explain how it differs from existing models
5. Curator reviews against quality bar
6. Merge or reject with explanation

**Auto-Rejected PRs:**
- Missing required fields
- Schema validation fails
- Not in LiteLLM docs (for cloud models)
- No benchmarks (for local models)
- Duplicate of existing model

## Validation and CI

### Automated Validation (GitHub Actions)

1. PR submitted with new/modified model file
2. CI validates JSON against schema
3. CI checks required fields present
4. CI verifies URL formats (model_uri, etc.)
5. CI passes/fails PR

### Manual Testing (Curator)

- Test cloud model API endpoint
- Test local model download from HuggingFace
- Verify benchmarks match published data
- Check pricing against provider website

## Deprecation Strategy

### Graceful Sunset

1. Set `"deprecated": true` in model JSON
2. Set `"replacement": "recommended-alternative"`
3. Keep file in repository (don't delete)
4. Gallery UI shows deprecation warning
5. Render engine still works for existing deployments
6. New users warned to choose replacement

**Users with deprecated models:**
- Existing blueprints still render (backwards compatible)
- Warning in gallery: "This model is deprecated. Consider gpt-5 instead."
- CLI shows: `leger models audit` → "You're using 1 deprecated model"

## Maintenance Time Investment

**Monthly:** 15 minutes
- Check for new releases
- Add 1-3 new models
- Update pricing if changed

**On-Demand:** 2-5 minutes
- Deprecate sunset model
- Fix metadata error
- Update model description

**Quarterly:** 30 minutes
- Full audit of all models
- Remove unused deprecated models
- Update benchmarks if new data available

## Current Model Inventory

### Cloud Models (11 models)

**OpenAI (4 enabled):**
- gpt-5, gpt-5-mini, gpt-5-nano (enabled)
- gpt-5-pro (disabled - premium tier)

**Anthropic (2 enabled):**
- claude-sonnet-4-5, claude-opus-4-1

**Google (2 enabled):**
- gemini-2.5-flash, gemini-2.5-pro

**OpenRouter (2 disabled):**
- grok-4-fast, deepseek-chat-v3.1

**Groq (1 disabled):**
- gpt-oss-120b-groq

### Local Models (10 models)

**Task Group (2 enabled, 2 disabled):**
- qwen3-0.6b, qwen3-4b (enabled)
- qwen3-14b, granite-4.0-h-micro (disabled)

**Heavy Group (2 enabled, 3 disabled):**
- gpt-oss-20b, gpt-oss-120b (enabled)
- qwen3-235b, llama-4-scout-17b, qwen3-coder-30b (disabled)

**Embeddings Group (1 enabled):**
- qwen3-embedding-8b (enabled, default)

## Support

For questions or issues:
- Open an issue in this repository
- Check the design document: [Model Store Architecture](../docs/model-store-architecture.md)
- Contact: Leger AI Team

---

**Last Updated:** 2025-10-22
**Schema Version:** 1.0
