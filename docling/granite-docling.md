

IBM Granite-Docling: End-to-end document understanding with one tiny model
Docling art
A different way to digest documents
Multilingual understanding
Granite-Docling and the Docling library
What's next for Docling?
Get started with Granite-Docling
Authors
Abraham
Abraham Daniels
Sr. Technical Product Manager, Granite

IBM

Dave
Dave Bergmann
Staff Writer, AI Models

IBM Think

Today, IBM is releasing Granite-Docling-258M, an ultra-compact and cutting-edge open-source vision-language model (VLM) for converting documents to machine-readable formats while fully preserving their layout, tables, equations, lists and more. It’s now available on Hugging Face through a standard Apache 2.0 license.

Granite-Docling is purpose-built for accurate and efficient document conversion, unlike most VLM-based approaches to optical character recognition (OCR) that aim to adapt large, general-purpose models to the task. Even at an ultra-compact 258M parameters, Granite-Docling’s capabilities rival those of systems several times its size, making it extremely cost-effective. The model goes well beyond mere text extraction: it handles both inline and floating math and code, excels at recognizing table structure and preserves the layout and structure of the original document. Whereas conventional OCR models convert documents directly to Markdown and lose connection to the source content, Granite-Docling’s unique method of faithfully translating complex structural elements makes its output ideal for downstream RAG applications.

Granite-Docling was developed by the team behind the celebrated open source Docling library, which turned one year old earlier this month. Docling provides tools, models and a command-line interface for document conversion, as well as plug-and-play integration with agentic AI workflows. Whereas the Docling library enables customizable ensemble pipelines, Granite-Docling is a single 258M parameter VLM that parses and processes documents in one shot.

The new Granite-Docling is a product-ready evolution of the experimental SmolDocling-256M-preview model released by IBM Research in partnership with Hugging Face in March 2025. Granite-Docling replaces the SmolLM-2 language backbone used for SmolDocling’s with a Granite 3-based architecture and replaces the SigLIP visual encoder with the updated SigLIP2, but otherwise retains the general methodology of SmolDocling (while exceeding its performance).

Crucially, Granite-Docling addresses certain instabilities present in SmolDocling-256M-preview, such as the occasional tendency to get stuck in loops of repeating the same token at a certain spot of a page. While some imperfections are inevitable from any model, reliable enterprise use at scale requires the confidence that no individual errors will derail the workflow itself. IBM Research mitigated these instabilities for Granite-Docling through extensive dataset filtering and cleaning to remove samples with inconsistent or missing annotations, as well as any samples with irregularities that introduced counterproductive ambiguities.

Like SmolDocling before it, Granite-Docling accurately captures document content and structure at a fraction of the computational requirements of most competitive offerings. Performance evaluations on common document understanding benchmarks are provided in Granite-Docling-258M’s Hugging Face model card.

A different way to digest documents
Central to Granite-Docling’s efficacy is DocTags, a universal markup format developed by IBM Research that captures and describes all page elements—charts, tables, forms, code, equations, footnotes, captions and more—as well as their contextual relation to one another and location within a document layout.

General-purpose markup languages like HTML or Markdown weren’t designed for image-to-sequence tasks like document conversion and have a limited vocabulary to describe the very specific attributes needed to accurately render many common elements of PDFs, slide decks and infographics. As such, direct conversion to common markup languages is typically lossy and ambiguous, increasing total token count and limiting the ability to preserve structural elements.

DocTags define a structured vocabulary of unambiguous tags and rules that explicitly separate textual content from document structure, minimizing both confusion and token usage. This enables Granite-Docling to isolate each element, describe its specific location on the page, and then perform OCR within it. It can also concisely describe relationships between different elements, such as proper reading order or hierarchy—for instance, linking a caption to its corresponding figure/table.

Diagram of DocTags, the output format of Granite-Docling
DocTags’ structured output, as demonstrated in the original SmolDocling paper (https://arxiv.org/abs/2503.11576), which has been accepted at the International Conference on Computer Vision (ICCV 2025).

DocTags is optimized for LLM readability. After Granite-Docling has output the original document(s) in DocTags, it can be easily converted directly into Markdown, JSON or HTML (or fed into a Docling library pipeline), streamlining the process of converting proprietary documents into high-quality datasets for fine-tuning other LLMs or enhancing LLM responses through retrieval augmented generation (RAG).

Multilingual understanding
SmolDocling-256-preview was trained on an English-language corpus, but it can reasonably handle documents authored in any language that uses standard Latin characters. After all, the model only needs to be able to parse and transcribe the document’s text—not (necessarily) understand it. But this obviously omits languages that don’t use Latin script, which limits SmolDocling’s utility in many parts of the world.

IBM’s intent is to make Granite-Docling as universally helpful as possible. To that end, Granite-Docling offers experimental multilingual capabilities across additional target languages that include Arabic, Chinese and Japanese, with the goal of extending Granite-Docling to more of the world’s most widely used alphabets.

Though these multilingual capabilities are in an early, experimental stage and have not yet been validated for enterprise-ready performance or stability, they represent an essential step toward the broadening of Granite-Docling's global utility. Expanding and strengthening Granite-Docling's multilingual capabilities will be a key priority for future iterations of the Docling ecosystem.

Granite-Docling and the Docling library
Granite-Docling is intended to complement the Docling library, rather than replace or supersede it. Each has their own particular strengths and use cases. To obtain optimal results, we recommend using Granite-Docling within the Docling framework.

The Docling library is a fully customizable software layer for building ensemble pipelines out of specialized models—like Tableformers, code parsers, equation parsers, vision models, ASR models, dedicated OCR models and generalist LLMs—for document conversion. The Granite-Docling model itself can serve as part of a larger VLM pipeline in Docling. The Docling library’s toolkit also directly facilitates integration with external services, like vector databases or agentic workflows. As such, the Docling library generally provides greater customization and the ability to select from a variety of models to suit one’s purpose.

Granite-Docling can provide an invaluable addition to Docling pipelines, replacing multiple single-purpose models with a compact VLM that consolidates key features—including multilingual, structure- and layout-preserving parsing of both natural language and an array of data modalities like code and complex equations—into a single model specialized for document version.

Theoretically speaking, converting documents in a single pass also reduces the potential for error accumulation. For instance, whereas a mislocated table at an early stage in an ensemble pipeline might distort or derail the ability to extract the table’s content in later stages, Granite-Docling will correctly reproduce a table even if it’s in the wrong location. That said, using it within the larger Docling framework combines the remarkable accuracy and cost-efficiency of the model itself with the customization, integration and error handling functions of the Docling library.

What's next for Docling?
The development of both Granite-Docling and the Docling library have been, and will continue to be, guided by feedback from the vibrant Docling community. As with its SmolDocling predecessor, IBM Research’s goal in releasing the new Granite-Docling model is to gather community feedback that can guide the continuous refinement and expansion of Docling capabilities for future releases.

Ongoing or planned initiatives for Docling include:

The continued development of the open source Docling-eval package for evaluating and comparing document understanding solutions. Central to these efforts is the curation of robust new evaluation datasets—some of which will remain unpublished to preclude “benchmaxxing”—and the creation of a standardized leaderboard informed in part by performance on these datasets.

Larger Granite-Docling models, in sizes of approximately 512M and 900M parameters. To prioritize speed and hardware flexibility, IBM Research intends to keep all future Granite-Docling models below a parameter count of 1B.

DocTags compatibility with models available in IBM watsonx.ai. DocTags samples will be included in the training data recipes of future IBM Granite language models and the specific corpus of DocTags terms will be added to the Granite tokenizer’s vocabulary. This will facilitate the smooth incorporation document data parsed by Granite-Docling into larger workflows orchestrated through IBM watsonx.
Get started with Granite-Docling
Granite-Docling-258M is now available through a standard Apache 2.0 license on Hugging Face. For more information about Granite-Docling, including performance evaluations on an array of document understanding benchmarks and instructions for running the model within a Docling pipeline, go to Granite-Docling’s Hugging Face model card.

To learn more about Docling and Granite-Docling, you can also visit docling.ai or check out the following tutorials and resources:

Article: IBM interview with Peter Staar, Principal Research Staff Member at IBM Research in Zurich and Chair, Docling Technical Steering Committee at the Linux Foundation
Tutorial: Build an AI-powered multimodal RAG system with Docling and Granite
Tutorial: Build a document-based question answering system by using Docling with Granite 3.1
Video: What is Docling?
Workshop: Docling Workshop
Explore Granite-Docling-258M →

https://huggingface.co/ibm-granite/granite-docling-258M
