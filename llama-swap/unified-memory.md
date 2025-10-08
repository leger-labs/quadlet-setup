Swapping between multiple frequently-used models are quite slow with llama-swap&llama.cpp. Even if you reload from vm cache, initializing is stil slow.

Qwen3-30B is large and will consume all VRAM. If I want swap between 30b-coder and 30b-thinking, I have to unload and reload.

Here is the key to load them simutaneouly: GGML_CUDA_ENABLE_UNIFIED_MEMORY=1.

This option is usually considered to be the method to offload models larger than VRAM to RAM. (And this option is not formally documented.) But in this case the option enables hotswap!

When I use coder, the 30b-coder are swapped from RAM to VRAM at the speed of the PCIE bandwidth. When I switch to 30b-thinking, the coder is pushed to RAM and the thinking model goes into VRAM. This finishes within a few seconds, much faster than totally unload & reload, without losing state (kv cache), not hurting performance.

My hardware: 24GB VRAM + 128GB RAM. It requires large RAM. My config:

  "qwen3-30b-thinking":
    cmd: |
      ${llama-server}
      -m Qwen3-30B-A3B-Thinking-2507-UD-Q4_K_XL.gguf
      --other-options
    env:
      - GGML_CUDA_ENABLE_UNIFIED_MEMORY=1

  "qwen3-coder-30b":
    cmd: |
      ${llama-server}
      -m Qwen3-Coder-30B-A3B-Instruct-UD-Q4_K_XL.gguf
      --other-options
    env:
      - GGML_CUDA_ENABLE_UNIFIED_MEMORY=1

groups:
  group1:
    swap: false
    exclusive: true
    members:
      - "qwen3-coder-30b"
      - "qwen3-30b-thinking"
You can add more if you have larger RAM.
