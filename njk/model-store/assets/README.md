# Model Store Assets

This directory contains provider logos and icons used in the model gallery UI.

## TODO: Provider Icons

The following provider icons need to be added:

### Cloud Providers
- [ ] `openai.svg` - OpenAI logo
- [ ] `anthropic.svg` - Anthropic logo
- [ ] `google.svg` - Google/Gemini logo
- [ ] `openrouter.svg` - OpenRouter logo
- [ ] `groq.svg` - Groq logo
- [ ] `xai.svg` - X.AI logo
- [ ] `deepseek.svg` - DeepSeek logo

### Local Model Families
- [ ] `qwen.svg` - Alibaba Qwen logo
- [ ] `llama.svg` - Meta Llama logo
- [ ] `mistral.svg` - Mistral AI logo
- [ ] `granite.svg` - IBM Granite logo
- [ ] `phi.svg` - Microsoft Phi logo
- [ ] `gemma.svg` - Google Gemma logo

## Icon Requirements

- **Format:** SVG preferred (scalable, small file size)
- **Size:** Square aspect ratio, 256x256px or larger
- **Style:** Clean, professional, recognizable
- **License:** Ensure proper licensing for logo use
- **Naming:** Lowercase with hyphens (e.g., `openai.svg`, `meta-llama.svg`)

## Usage in Model Definitions

Reference icons in model JSON files using the `icon` field:

```json
{
  "icon": "assets/openai.svg"
}
```

Gallery UI will display the icon alongside the model card.
