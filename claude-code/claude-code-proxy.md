https://github.com/1rgs/claude-code-proxy
since we already have litellm configured we can use claude code with proxy
So I have had FOMO on claudecode, but I refuse to give them my prompts or pay $100-$200 a month. So 2 days ago, I saw that moonshot provides an anthropic API to kimi k2 so folks could use it with claude code. Well, many folks are already doing that with local. So if you don't know, now you know. This is how I did it in Linux, should be easy to replicate in OSX or Windows with WSL.

Start your local LLM API

Install claude code

install a proxy - https://github.com/1rgs/claude-code-proxy

Edit the server.py proxy and point it to your OpenAI endpoint, could be llama.cpp, ollama, vllm, whatever you are running.

Add the line above load_dotenv
+litellm.api_base = "http://yokujin:8083/v1" # use your localhost name/IP/ports

Start the proxy according to the docs which will run it in localhost:8082

export ANTHROPIC_BASE_URL=http://localhost:8082

export ANTHROPIC_AUTH_TOKEN="sk-localkey"

run claude code

I just created my first code then decided to post this. I'm running the latest mistral-small-24b on that host. I'm going to be driving it with various models, gemma3-27b, qwen3-32b/235b, deepseekv3 etc


alternative: with https://github.com/musistudio/claude-code-router


Tartarus116
•
2mo ago
Got it to work, thx! My config for anyone wondering:

task "claude-code" {
      driver = "docker"
      config {
        image   = "node:20-alpine"
        command = "sh"
        args = [
          "-c",
          "npm cache clean --force && npm install -g u/anthropic-ai/claude-code && npm install -g u/musistudio/claude-code-router && ccr start"
        ]
        volumes = [
          "local/.claude-code-router/config.json:/root/.claude-code-router/config.json",
        ]
      }
      template {
        destination = "local/.claude-code-router/config.json"
        data = <<EOH
{
  "ANTHROPIC_BASE_URL": "http://localhost:3456",
  "ANTHROPIC_API_KEY": "sk-123456",
  "APIKEY": "sk-123456",
  "API_TIMEOUT_MS": 3600000,
  "NON_INTERACTIVE_MODE": false,
  "Providers": [
    {
      "name": "openai",
      "api_base_url": "http://gpustack.virtual.consul/v1/chat/completions",
      "api_key": "xxx",
      "models": [
        "qwen3-4b-instruct-2507-gguf"
      ],
      "transformer": {
          "use": [
            [
              "maxtoken",
              {
                "max_tokens": 4096
              }
            ]
          ]
        }
    }
  ],
  "Router": {
    "default": "openai,qwen3-4b-instruct-2507-gguf",
    "background": "openai,qwen3-4b-instruct-2507-gguf",
    "think": "openai,qwen3-4b-instruct-2507-gguf",
    "longContext": "openai,qwen3-4b-instruct-2507-gguf",
    "longContextThreshold": 4096,
    "webSearch": "openai,qwen3-4b-instruct-2507-gguf"
  }
}       
EOH        
      }
      resources {
        cpu    = 1000
        memory = 512
      }
    }
Then, launch a console with ccr code.
