At minimum i like the list of extracton models and embedding odels this provides. it does exemplify an ideal workflow of mine which is to process all my pdfs in one go and make them ready for RAG
https://github.com/kiln-ai/kiln

---

https://www.reddit.com/r/LocalLLaMA/comments/1nzskwx/kiln_rag_builder_now_with_local_open_models/

Hey everyone - two weeks ago we launched our new RAG-builder on here and Github. It allows you to build a RAG in under 5 minutes with a simple drag and drop interface. Unsurprisingly, LocalLLaMA requested local + open model support! Well we've added a bunch of open-weight/local models in our new release:

Extraction models (vision models which convert documents into text for RAG indexing): Qwen 2.5VL 3B/7B/32B/72B, Qwen 3VL and GLM 4.5V Vision

Embedding models: Qwen 3 embedding 0.6B/4B/8B, Embed Gemma 300M, Nomic Embed 1.5, ModernBert, M2 Bert, E5, BAAI/bge, and more

You can run fully local with a config like Qwen 2.5VL + Qwen 3 Embedding. We added an "All Local" RAG template, so you can get started with local RAG with 1-click.

Note: we’re waiting on Llama.cpp support for Qwen 3 VL (so it’s open, but not yet local). We’ll add it as soon as it’s available, for now you can use it via the cloud.

Progress on other asks from the community in the last thread:

Semantic chunking: We have this working. It's still in a branch while we test it, but if anyone wants early access let us know on Discord. It should be in our next release.

Graph RAG (specifically Graphiti): We’re looking into this, but it’s a bigger project. It will take a while as we figure out the best design.

Some links to the repo and guides:

Kiln AI on Github: >4k stars

Documents & Search (RAG) Docs/Guide

Kiln Discord

Homepage

I'm happy to answer questions if anyone wants details or has ideas! Let me know if you want support for any specific local vision models or local embedding models.
