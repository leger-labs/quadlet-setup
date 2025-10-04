A few people were asking yesterday if Open WebUI works with llama-swap. Short answer: Yes, and it's great! (imho)

So I wanted to make a video of the setup and usage. Today was my my first time installing Open WebUI and my first time connecting it to llama-swap. I've been using Librechat for a long time but I think I'll be switching over!

OWUI install was a single command one of my linux boxes:

docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
In the video:

llama-swap's UI is on the left and Open WebUI on the right

A new Connection is created in OWUI's Admin Settings

Open WebUI automatically downloads the list of models. llama-swap extends the /v1/models endpoint to add both names and descriptions.

Initiating a new chat automatically loads the GPT OSS 120B model

The response is regenerated with a different model (qwen3 coder) and llama-swap handles this without any surprises.

I'd be happy to answer any questions about llama-swap. The length of the video (~6min) is my whole experience with OWUI so I probably can't help much with that :)

My LLM server hardware: 2x3090, 2xP40, 128GB of DDR4 RAM. Also thanks to the contributors of llama.cpp and OWUI! Really amazing projects!

---

https://github.com/mostlygeek/llama-swap/pkgs/container/llama-swap

Recent tagged image versions
v162-intel-b6665
intel
Published about 6 hours ago · Digest …
2Version downloads
v162-cuda-b6665
cuda
Published about 6 hours ago · Digest …
85Version downloads
v162-musa-b6665
musa
Published about 6 hours ago · Digest …
0Version downloads
v162-vulkan-b6665
vulkan
Published about 6 hours ago · Digest …
33Version downloads
cpu
Published about 6 hours ago · Digest …
11Version downloads
View all tagged versions
README.md
llama-swap header image GitHub Downloads (all assets, all releases) GitHub Actions Workflow Status GitHub Repo stars

llama-swap
llama-swap is a light weight, transparent proxy server that provides automatic model swapping to llama.cpp's server.

Written in golang, it is very easy to install (single binary with no dependencies) and configure (single yaml file). To get started, download a pre-built binary, a provided docker images or Homebrew.

Features:
✅ Easy to deploy: single binary with no dependencies
✅ Easy to config: single yaml file
✅ On-demand model switching
✅ OpenAI API supported endpoints:
v1/completions
v1/chat/completions
v1/embeddings
v1/audio/speech (#36)
v1/audio/transcriptions (docs)
✅ llama-server (llama.cpp) supported endpoints:
v1/rerank, v1/reranking, /rerank
/infill - for code infilling
/completion - for completion endpoint
✅ llama-swap custom API endpoints
/ui - web UI
/log - remote log monitoring
/upstream/:model_id - direct access to upstream HTTP server (demo)
/unload - manually unload running models (#58)
/running - list currently running models (#61)
/health - just returns "OK"
✅ Run multiple models at once with Groups (#107)
✅ Automatic unloading of models after timeout by setting a ttl
✅ Use any local OpenAI compatible server (llama.cpp, vllm, tabbyAPI, etc)
✅ Reliable Docker and Podman support using cmd and cmdStop together
✅ Full control over server settings per model
✅ Preload models on startup with hooks (#235)
How does llama-swap work?
When a request is made to an OpenAI compatible endpoint, llama-swap will extract the model value and load the appropriate server configuration to serve it. If the wrong upstream server is running, it will be replaced with the correct one. This is where the "swap" part comes in. The upstream server is automatically swapped to the correct one to serve the request.

In the most basic configuration llama-swap handles one model at a time. For more advanced use cases, the groups feature allows multiple models to be loaded at the same time. You have complete control over how your system resources are used.

config.yaml
llama-swap is managed entirely through a yaml configuration file.

It can be very minimal to start:

models:
  "qwen2.5":
    cmd: |
      /path/to/llama-server
      -hf bartowski/Qwen2.5-0.5B-Instruct-GGUF:Q4_K_M
      --port ${PORT}
However, there are many more capabilities that llama-swap supports:

groups to run multiple models at once
ttl to automatically unload models
macros for reusable snippets
aliases to use familiar model names (e.g., "gpt-4o-mini")
env to pass custom environment variables to inference servers
cmdStop for to gracefully stop Docker/Podman containers
useModelName to override model names sent to upstream servers
healthCheckTimeout to control model startup wait times
${PORT} automatic port variables for dynamic port assignment
See the configuration documentation in the wiki all options and examples.

Reverse Proxy Configuration (nginx)
If you deploy llama-swap behind nginx, disable response buffering for streaming endpoints. By default, nginx buffers responses which breaks Server‑Sent Events (SSE) and streaming chat completion. (#236)

Recommended nginx configuration snippets:

# SSE for UI events/logs
location /api/events {
    proxy_pass http://your-llama-swap-backend;
    proxy_buffering off;
    proxy_cache off;
}

# Streaming chat completions (stream=true)
location /v1/chat/completions {
    proxy_pass http://your-llama-swap-backend;
    proxy_buffering off;
    proxy_cache off;
}
As a safeguard, llama-swap also sets X-Accel-Buffering: no on SSE responses. However, explicitly disabling proxy_buffering at your reverse proxy is still recommended for reliable streaming behavior.

Web UI
llama-swap includes a real time web interface for monitoring logs and models:

image
The Activity Page shows recent requests:

image
Installation
llama-swap can be installed in multiple ways

Docker
Homebrew (OSX and Linux)
From release binaries
From source
Docker Install (download images)
Docker images with llama-swap and llama-server are built nightly.

# use CPU inference comes with the example config above
$ docker run -it --rm -p 9292:8080 ghcr.io/mostlygeek/llama-swap:cpu

# qwen2.5 0.5B
$ curl -s http://localhost:9292/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer no-key" \
    -d '{"model":"qwen2.5","messages": [{"role": "user","content": "tell me a joke"}]}' | \
    jq -r '.choices[0].message.content'

# SmolLM2 135M
$ curl -s http://localhost:9292/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer no-key" \
    -d '{"model":"smollm2","messages": [{"role": "user","content": "tell me a joke"}]}' | \
    jq -r '.choices[0].message.content'
Docker images are built nightly with llama-server for cuda, intel, vulcan and musa.
They include:

ghcr.io/mostlygeek/llama-swap:cpu
ghcr.io/mostlygeek/llama-swap:cuda
ghcr.io/mostlygeek/llama-swap:intel
ghcr.io/mostlygeek/llama-swap:vulkan
ROCm disabled until fixed in llama.cpp container
Specific versions are also available and are tagged with the llama-swap, architecture and llama.cpp versions. For example: ghcr.io/mostlygeek/llama-swap:v89-cuda-b4716

Beyond the demo you will likely want to run the containers with your downloaded models and custom configuration.

$ docker run -it --rm --runtime nvidia -p 9292:8080 \
  -v /path/to/models:/models \
  -v /path/to/custom/config.yaml:/app/config.yaml \
  ghcr.io/mostlygeek/llama-swap:cuda
Homebrew Install (macOS/Linux)
The latest release of llama-swap can be installed via Homebrew.

# Set up tap and install formula
brew tap mostlygeek/llama-swap
brew install llama-swap
# Run llama-swap
llama-swap --config path/to/config.yaml --listen localhost:8080
This will install the llama-swap binary and make it available in your path. See the configuration documentation

Pre-built Binaries (download)
Binaries are available for Linux, Mac, Windows and FreeBSD. These are automatically published and are likely a few hours ahead of the docker releases. The binary install works with any OpenAI compatible server, not just llama-server.

Download a release appropriate for your OS and architecture.
Create a configuration file, see the configuration documentation.
Run the binary with llama-swap --config path/to/config.yaml --listen localhost:8080. Available flags:
--config: Path to the configuration file (default: config.yaml).
--listen: Address and port to listen on (default: :8080).
--version: Show version information and exit.
--watch-config: Automatically reload the configuration file when it changes. This will wait for in-flight requests to complete then stop all running models (default: false).
Building from source
Build requires golang and nodejs for the user interface.
git clone https://github.com/mostlygeek/llama-swap.git
make clean all
Binaries will be in build/ subdirectory
Monitoring Logs
Open the http://<host>:<port>/ with your browser to get a web interface with streaming logs.

CLI access is also supported:

# sends up to the last 10KB of logs
curl http://host/logs'

# streams combined logs
curl -Ns 'http://host/logs/stream'

# just llama-swap's logs
curl -Ns 'http://host/logs/stream/proxy'

# just upstream's logs
curl -Ns 'http://host/logs/stream/upstream'

# stream and filter logs with linux pipes
curl -Ns http://host/logs/stream | grep 'eval time'

# skips history and just streams new log entries
curl -Ns 'http://host/logs/stream?no-history'
Do I need to use llama.cpp's server (llama-server)?
Any OpenAI compatible server would work. llama-swap was originally designed for llama-server and it is the best supported.

For Python based inference servers like vllm or tabbyAPI it is recommended to run them via podman or docker. This provides clean environment isolation as well as responding correctly to SIGTERM signals to shutdown.
