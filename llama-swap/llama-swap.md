wrapper around ramamalama models, middle layer between litellm and ramalama containers. Bring over perplexity chat insights here, middle layer between litellm and ramalama containers. 

---

If you have Docker Compose v2.23.1 or higher you can manage llama-swap's config.yaml directly in your docker-compose.yaml. This makes llama-swap extremely reproducible as there is no need to mount config.yaml, make changes and restart the container.

For CUDA the docker-compose.yaml can look something like this.
```
configs:
  llama-swap-config:
    content: |
      # From here is where you define the config for llama-swap.
      healthCheckTimeout: 3600 # Set it to one hour so model downloads don't stop halfway through.
      
      macros:
        "latest-llama": >
          /app/llama-server
          --port 9999

      models:
        "Qwen3-32B-GGUF:UD-Q4_K_XL":
          proxy: "http://127.0.0.1:9999"
          cmd: >
            $${latest-llama}
            -hf unsloth/Qwen3-32B-GGUF:UD-Q4_K_XL
            -ngl 99
            --ctx-size 8192
            --jinja
            --flash-attn
        
        "Qwen3-30B-A3B-Instruct-2507-GGUF:UD-Q4_K_XL":
          proxy: "http://127.0.0.1:9999"
          cmd: >
            $${latest-llama}
            -hf unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF:UD-Q4_K_XL
            -ngl 99
            --ctx-size 8192
            --jinja
            --flash-attn
            
        "gemma-3-27b-it-GGUF:UD-Q4_K_XL":
          proxy: "http://127.0.0.1:9999"
          cmd: >
            $${latest-llama}
            -hf unsloth/gemma-3-27b-it-GGUF:UD-Q4_K_XL
            -ngl 99
            --ctx-size 8192
            --jinja
            --flash-attn

services:
  llama-swap:
    image: ghcr.io/mostlygeek/llama-swap:cuda # Change this to vulkan, cpu etc.
    ports:
      - '9292:8080'
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - capabilities:
                - gpu
              count: all
              driver: nvidia # Remove this line if using AMD/Vulkan.
    configs:
      - source: llama-swap-config # Takes the content of the llama-swap-config variable
        target: /app/config.yaml  # and writes it to this file.
    volumes:
      - ./models:/root/.cache/llama.cpp/
```


