The Open WebUI RAG Conundrum: Chunks vs. Full Documents

demodomain
. February 20, 2025
 19,733 Views
Shares
UPDATE 23rd Feb 2025… At the end of this post, I outline a solution to the problem.
 
On Reddit, and elsewhere, a somewhat “hot” topic is using OWUI to manage a knowledge base / files and take advantage of OWUI’s built-in RAG (Retrieval Augmented Generation) functionalities. The thing is, sometimes, you’re not trying to retrieve snippets for context; you’re aiming for summarization, translation, file comparison, or brainstorming. I often see people struggling with system prompts or RAG prompts to get an LLM do process documents in ways that RAG simply doesn’t support. You can’t “chat to your PDF” and ask, “Take the grand totals section from my Excel file and re-write the summary in the financial report to reflect those numbers.” RAG isn’t built for this. It’s built to merely return chunks of text to the Agent that are hopefully semantically similar to the user’s request.
 
In these cases, feeding the LLM the whole document is crucial, not just chunks.
 
OpenWeb UI is great for document storage and a chat interface, and RAG configuration options but you can’t disable RAG. Wouldn’t it be nice to be able to switch between RAG (chunks), full document text, and even full document as a binary file / base64 file so when, for example, you want to send a whole PDF to Google Gemini for parsing (as opposed to just the extracted text from a RAG process), you can?
 
In my custom setups, I’ve built in toggles to choose between full documents and RAG chunks, or even dual vector databases (one for small chunks, one for huge “chunks”) and I simply don’t use OWUI for RAG. But I was hoping I could perhaps use OWUI as a front-end, allowing the user to decide between chunks and full documents as they wish, and then having a custom pipe to send the user’s prompt + chunks (or full document) to whatever platform they like (in my case, n8n). But to doing this cleanly in Open WebUI turned out to be trickier than expected.
 
The point of this post is to see if OpenWeb UI can be tweaked (ok, wrestled) into submission to allow the user the flexibility to choose between RAG or full document context. It’s not to provide a “template” of a solution because when it comes to document management (RAG), there is no turnkey solution. So instead this post outlines the technical possibilities and I hope that you can take the knowledge and weave your own solution.
 
For non-tech users who want to use OpenWeb UI and avoid RAG, a simple workaround is cranking up the chunk size to something massive (like a million tokens if you’re using Google Gemini) or whatever your LLM’s context window can handle. This effectively gives you one chunk per document – basically the same as “full document” for most scenarios. The problem? Open WebUI’s chunking settings are global. You can’t just tweak it on the fly. This is fine if you always want full documents passed to the LLM and I think a massive chunk size in this scenario is fine as it allows you to use all the benefits of OpenWeb UI and kinda “bypass” RAG.
 
And for those who want to tell me that massive chunk sizes in RAG is a “no no”, this is my response:
 

 
Perhaps that reference shows my age! But I’ve really found no issue with manipulating RAG settings to send massive chunks when there’s simply no other alternative.
 
I also often see questions – and negative comments – about OWUI’s RAG implementation. So to start with, I wanted to also look into exactly how they do it. I’ll first outline how it works and then go onto how I tried to bypass it.
 
My opinion, on a cursory look at their code is they handle RAG pretty damn well so I’m not sure what the negative comments are about.
 
Open Web UI’s RAG implementation
Open WebUI’s RAG implementation relies on several components working together:
 
Document Processing and Storage:
Uploaded files are processed using Langchain document loaders. Different loaders are used based on file type (PDF, CSV, RST, etc.). For web pages a WebBaseLoader is used.
After loading, the documents are split into chunks using either a character-based or token-based text splitter (Tiktoken is used for the latter) with configurable chunk size and overlap.
These chunks are embedded using a SentenceTransformer model, chosen through settings or defaults to sentence-transformers/all-MiniLM-L6-v2. Ollama and OpenAI embedding models are also supported.
The embeddings, along with the document chunks and metadata, are stored in a vector database. Chroma, Milvus, Qdrant, Weaviate, Pgvector and OpenSearch are supported.
Query Generation:
When a user submits a query, a separate LLM call is made to generate search queries based on the conversation history.
This uses a configurable prompt template, but by default encourages generating broad, relevant queries unless there’s absolute certainty no extra data is needed.
This step can be disabled through admin settings if not desired.
Retrieval:
The generated search queries are used to retrieve relevant chunks from the vector database. The default setting combines BM25 search and vector search.
BM25 provides a keyword-based search, while vector search compares the query embedding with the stored chunk embeddings.
Optionally, retrieved chunks can be reranked using a reranking model (like a CrossEncoder) and a relevance score threshold is applied to filter results based on similarity.
Context Injection:
The retrieved relevant contexts (chunks with metadata) are formatted into a single string.
This string, along with the original user query, is injected into a prompt template designed for RAG.
This template is configurable but defaults to one that instructs the LLM to answer the query using the context and include citations when a <source_id> tag is present.
LLM Response Generation:
The final prompt, including context and user query, is sent to the chosen LLM.
The LLM’s response, which may include citations based on the provided context, is then displayed to the user.
Key Files:
routers/retrieval.py: Handles the API endpoints for document processing, web search, and querying the vector database.
retrieval/loaders/main.py: Contains the logic for loading documents from different file types.
retrieval/vector/main.py: Defines the interface for vector database interaction and includes implementations for Chroma and Milvus.
retrieval/vector/connector.py: Selects the specific vector database client based on configured settings.
utils/task.py: Contains helper functions for prompt templating, including rag_template.
In short, Open Web UI’s RAG uses a multi-step process involving query generation, hybrid search (BM25 + vector search), reranking, context preparation, and finally, LLM response generation. This process is highly configurable, allowing users to fine-tune each step to their specific needs.
 
Ways to get files into OpenWeb UI
Just so everyone is on the same page about what’s possible, I thought I’d outline the options:

Drag and drop a file into the prompt.
If it’s a document (not an image) it will get ragged into a temporary knowledge base called “uploads”.
But… you can click on the file and select “Using Focused Retrieval” which means “send the full content, not chunks” – awesome.
Create a knowledge base, add your files. Then link the knowledge base to your model (see my post on creating your own CustomGPT in OWUI).
Your documents will get RAGged. Nothing you can do about it.
Same as option (2) above, but you don’t link the knowledge base to your model. When you want to send one or more files, enter # as the first character of your prompt and select from the knowledge base one or more files (or the whole knowledge base, if you like).
Again, everything is RAGged.
The Open WebUI RAG Roadblock
If you’re only dealing with images, there’s no issue because images can’t be RAGged and are therefore embedded directly in the prompt’s JSON structure as base64 data:
 
{
  “stream”: true,
  “model”: “some model”,
  “messages”: [
    {
      “role”: “user”,
      “content”: [
        {
          “type”: “text”,
          “text”: “hello there”
        },
        {
          “type”: “image_url”,
          “image_url”: {
            “url”: “data:image/png;base64,iVBORw…”
          }
        }
      ]
    }
  ]
}
 
This structure, generated within open_webui/utils/middleware.py, allows a custom pipe to easily capture and process the image data.
 
If you drag-and-drop documents into the prompt, this is where the RAG inflexibility becomes a major problem. Open WebUI intercepts the document, performs RAG, and never exposes the original file data to the custom pipe until after it’s taken your prompt, performed a RAG search, retrieved the chunks, and injected those chunks + a system prompt into your conversation which tells the model to use the chunks when answering your question.
 
This means it’s not simply a matter of reading in the original files and sending the full content (text or binary) to wherever you want because you also have to deal with the injection of chunks and RAG template into your pipe / messages.
 
Here’s the logic flow:
User Input: The user types something into the chat input.

Middleware (in open_webui/backend/middleware.py):

The request goes through middleware, specifically process_chat_payload.

process_chat_payload is where the RAG logic is always applied, regardless of whether a custom pipe is being used.

It checks for features.web_search, features.image_generation, and features.code_interpreter to see if those should be enabled.

Crucially, it always calls get_sources_from_files if there are any files. This function is the heart of the RAG system.

The RAG template (RAG_TEMPLATE) is always prepended to the first user message, or a system prompt is added if one doesn’t exist.

get_sources_from_files (in open_webui/backend/retrieval/main.py)

With the file upload options of “Using Focused Retrieval”, the way OWUI sends the full content to your pipe is exactly the same way it sends RAG chunks to your pipe. It uses the same back-end RAG pipeline, simply skipping the RAG vector search, and jumping straight to injecting into your pipe / messages the RAG template and this time the full content.
 
And… there’s a problem if your model is connected to a knowledge base. I think a common use-case is where people want a knowledge base but occasionally want to upload a file when the conversation requires more focussed attention by the LLM on a specific document.
 
But while you might have the reasonable assumption that uploading a file (and even toggled to use full content) will make it the “focus” of the current discussion, OWUI simply throw that file into the mix with all other knowledge base files before a RAG search is done. It’s therefore possible that the file you uploaded won’t even be included in the search results! You have no control over indicating to OWUI that your uploaded file is more important that the knowledge base files. And you can’t disable the knowledge base on a turn-by-turn basis.
 
Regardless, once OWUI has done its search and provided your pipe with the chunks and file IDs, you can fetch the full document content via the /api/v1/files/{id}/content endpoint (defined in open_webui/routers/files.py).
However, the prompt still contains the RAG chunks, necessitating manual removal to avoid redundancy – a clumsy workaround.
 
The latest release of OWUI (Feb 2025) now includes a setting, “Full Context Mode”, where you can specify whether you want “full documents” or RAG. This achieves the same result as setting “Using Focused Retrieval” on a file-by-file bases for files you’ve uploaded into the prompt.
 
However, there’s a catch. The new feature is controlled by a boolean setting in the backend configs RAG_FULL_CONTEXT, which unfortunately means it’s global.
 
This means users can’t select on a file-by-file basis, or a prompt-by-prompt basis, or even a model-by-model basis to send full files, or chunks from the RAG query.
 
This setting impacts how the get_sources_from_files function in retrieval.utils operates…
If RAG_FULL_CONTEXT is True, then the entire document is returned from all specified sources. The context returned from the function does NOT get chunked or embedded but still only returns the text content from the document (no binary or base64 of the file can be accessed by a pipe)
If RAG_FULL_CONTEXT is False (the default), then chunks are retrieved as before. The number of chunks can be configured via the RAG_TOP_K config setting. The function will then call the embedding function and use that as your query embeddings in the vector db.
And, just like when you upload a file and set “Using Focused Retrieval”, OWUI still uses the internal RAG pipeline, even though it’s sending the full contents of the document. So again, there’s no way to intercept the document in a pipe and do something with it before the RAG search has taken place and injected chunks into your chat history.
 
I’ve tested all workarounds that I can think of, using pipes, filters, inlets… there’s no solution to be found where a custom-written pipe can avoid / disable / block OWUI’s internal RAG pipeline from triggering and modifying your prompts before your pipe is even called – unless it’s a file that can’t be RAGged (eg; image files).
 
But also… OWUI uses your pipe as a host for this:
A pipe is considered a model by OWUI. So, your custom pipe, being a model is used by OWUI to generate a nice title for your chat / conversation. It does this by sending to the model (your pipe) a request for the LLM to look at the first prompt from the user and come up with a nice title with an emoji or two.
 
Luckily, this can be switched off in settings but you still need to cater for the possibility it’s not switched off:
 
# Check if this is a chat title generation request
     if “### Task:\nAnalyze the chat history” in system_content:
          print(“Detected chat title generation request, skipping…”)
          return {“messages”: messages}
A Workable Workaround (Minimal Core Modification)
One possible (untested) solution involves a minor change to the core process_chat_payload function. This modification ensures that the entire file-handling logic (including chunking and vector database lookup) is skipped if the “!” prefix is present. Critically, it preserves the original file information and passes it along to the custom pipe via the knowledge parameter in extra_params.
 
open_webui/utils/middleware.py (Simplified)
 
async def process_chat_payload(request, form_data, metadata, user, model):
# … other code
 
if user_message is not None and user_message.startswith(“!”):
bypass_rag = True
extra_params[“__knowledge__”] = metadata.get(“files”, []) # Preserving original files
if not bypass_rag:
# … (Original file handling logic to be skipped)
pass
# … rest of process_chat_payload …
 
This modified process_chat_payload effectively acts as a true “bypass RAG” switch, giving your custom pipe complete control over how file content is handled.
 
While this modification requires touching the core code (which isn’t ideal), it’s a targeted – and quite small – change that may resolve the conflict between OWUI’s internal processing and your custom pipe’s intended behavior.
 
Hopefully, future versions of Open WebUI will include more robust mechanisms for dynamically controlling RAG and accessing full file content directly, eliminating the need for any workarounds. Until then, you’ll need to drag and drop files into your prompt as required as those will be sent, in full, to the LLM.
 
LATEST UPDATE 23rd Feb 2025…

The Final Solution: Breaking Free from the Flying Dutchman
I’ve re-written this blog post 3 times as each day I find new information and discover possible solutions.

OWUI’s forcing of RAG, even with options for “full documents” felt quite like the tale of Bootstrap Bill Turner and Davy Jones. OpenWebUI’s RAG system can be an unwanted passenger, binding itself to my custom pipe like Bootstrap Bill bound to the Flying Dutchman. Every time I tried to process a document, OpenWebUI’s RAG would inject itself into the process, like a symbiotic entity I couldn’t shake off. I needed to stop it somehow.

Here’s what I’ve now implemented in a rather complex and long pipe – but remember how at the start of this post I mentioned how everyone has a very specific environment, and tech stack, and use-case when it comes to RAG? Well I do to. I want to be able to connect to all unsupported models (Perplexity, Google, Anthropic) and also connect OWUI to an n8n workflow. And I have very specific requirements about how the prompt, conversation history, documents (chunks, full text, binary) are handled depending on the model.

So it’s just too convoluted to share as people will inevitably have questions and there’s a limit to the time I can put in. But I do have demos of pipes and n8n workflows on my github that comprise the concepts I’ve discussed in here. It’s just that final solution is very much coded for my use-case, and it’s 1,500 lines long.

I encourage you to take what I’ve learned, look at the demos I have, and build out your own solution suitable specifically for you.

Here’s what I implemented:
Firstly, my pipe looks at all settings and if the settings are such that the internal RAG pipeline will return actual “chunks” instead of full document “chunks” then the pipe knows that the “chunks” that are attached to the RAG template and injected into the pipe / messages are in fact actual “chunks”. Otherwise it knows the chunks are full document “chunks”.
In addition it looks at the <source_id> tags that OWUI uses when injecting chunks into the prompt, to work out what the exact file is that’s related to each chunk. It then adds a new tag into the results, <filename>. This means the user can actually mention a filename to the model and the model will know where to look
If actual chunks are being returned, then the pipe then checks if the first character of the user prompt is the “-” character, and if it’s there, this is essentially a message from the user saying, “I want to disable all RAG for this turn of the conversation.” So the pipe strips out the chunks, and the RAG template entirely from the prompt – only the user’s prompt, chat history, and system message are sent.
If actual chunks are being returned, and there’s no “-” as the first character of the use prompt, the pipe then checks if the first character of the user prompt is the “!” character, and if it’s there, this is a message from the user saying, “I want full document text to be sent on this turn of the conversation.” So the pipe strips out the chunks, reads in the actual file contents, and inserts the full content to where the chunks were
The method to get the right metadata to get the file ID is different depending on whether the chunks are returned from a file in the knowledge base or from a file that was uploaded in to the prompt.
For Google, Anthropic, and Perplexity, if it’s an image, it grabs the base64 (which is easy because it’s just part of the user input) and sends it along to those models.
NOTE: image files can’t be put into a knowledge base and you can’t select an image file and toggle on “Using Focused Retrieval” because there’s no text content in an image (obviously) so OWUI (obviously) doesn’t trigger any RAG processes
For Google, if the chunk refers to a PDF and the settings are such that the user wants full content, and the valve is set to perform the following function, the actual binary of the PDF is sent to Google because I like how Google does PDF OCR.
For n8n, I want to handle all RAG, and all chat history. (I’m using OWUI as an interface, my logic layer is all n8n, and my data layer is Supabase). So, regardless of any settings, any RAG process, or anything, it will:
read in the original file that’s part of the prompt (from the knowledge base, or uploaded, image or document) and sends the base64 of the file and the last user message to n8n
waits for a response, updating the status in OWUI every 2 seconds
updates the status in OWUI whenever n8n calls a tool or executes a sub-workflow
receives the response from n8n
extracts any <think> elements for display as collapsable elements in OWUI
displays the response + <think> element
Summary
With the OWUI-provided admin-level and uploaded file-level settings to use full content or not, combined with prompt-level ability to disable RAG (-), or force full content (!), and the fact that a single pipe handles multiple models plus an n8n workflow, I think I’ve finally proven to myself that is IS possible to… well, not work around, but work within OWUIs RAG implementation and get reasonable flexibility for switching between RAG chunks and full document chunks and binary files.

Technical Footnote

I discovered a bit of a challenging bug. Here’s how OWUI format the <source> and <source_id> tags:

<source>
<source>1</source_id>
content here
</source>

See the issue I’ve set to bold? That took about 6 hours to notice, wondering why my regex extraction of the “content” (<source>) kept failing!

---

Comments:
Thanks for the blog. The only issue is that with custom rag we need to duplicate the chunks generation process and other stuff (openwebui still perform it when you add a document into the chat + your eventually custom Rag backend) and this could add more latency and a worst user experience But, at least, we have a solution to improve the rag process. So thank you

Got some questions ( hope you would like to have a nice conversation about those topics):

Did you also understand how to handle citations?

Why don't use the __ files __ param in your function pipe() method?

Are you using pipelines or pipes?

Moreover, if you need to disable query generation for rag I think that, through admin settings, you can disable the toggle that start that particular process



Upvote
1

Downvote

Reply

Award

Share

u/Professional_Ice2017 avatar
Professional_Ice2017
OP
•
7mo ago
Yes, there's a double-RAG thing going on. I definitely didn't focus on how what I implemented could be used, or should be used. I got a little caught up in the technicalities of solving the conundrum.

But yes... 'what does it all mean in terms of real-world usage?' is a good question.

But a disclaimer... everyone has a different, justifiable use-case and RAG is so infinitely configurable and stackable that I prefer to avoid complicated use-case debates on forums like reddit (too much typing!!) :)

However, to touch on your points, because they are interesting...

- I did use __ files __ in my pipe.

- I'm just using a pipe.

- If you want to send off your OWUI document/s for external RAG processing, then yes, OWUI will still RAG your documents even if you don't want. But I still have a bit of confusion on this point:

- the new "Full context mode" in v0.5.15 is great, and in theory should disable RAG, right? But when I was testing last night, even with that option turned on, OWUI would still inject RAG prompts into my pipe... for what purpose? I have "Full context mode" on. I haven't looked into that. But surely... with that new option, it won't bother RAGging your document?!

But let's assume it does still RAG your docs. Yes, that's processing which is unnecessary, but only if you never want to use OWUI's RAG. I approached this from a perspective of making OWUI as flexible as possible as I'm exploring it for multiple use-cases. Specifically, "How can I decide between when I want to use full documents versus RAG - on a turn-by-turn basis, or perhaps a model-by-model basis?" If that's your use-case then great, you have OWUI RAG, and you can also send off for external RAG, or send a full PDF to Google for OCR... whatever you want; the choice is yours.

But let's assume you 100% don't want OWUI RAG and you just want to use OWUI has a sexy interface on some other back-end which handles RAG and / or AI Agent responses, etc... yes, OWUI is processing documents to RAG which is wasted processing but it happens upon upload; that's where the latency is. There's no (significant (depending on your use-case)) latency when OWUI calls your own pipe with a RAG prompt and you code your pipe to simply respond with "" (empty string) because your pipe is simply about grabbing the full document/s and processing them externally.

How someone pulls together the information I've provided on my Wordpress post is up to them; which is why I just outline the facts I've come across in perhaps a rather boring way. They're just some facts and I hope it helps in whatever problem you're trying to solve.



Upvote
2

Downvote

Reply

Award

Share

sir3mat
•
7mo ago
I really appreciate your effort and your blog post and the time you dedicate to answering me. Very good job



Upvote
2

Downvote

Reply

Award

Share

u/Professional_Ice2017 avatar
Professional_Ice2017
OP
•
7mo ago
With some fresh eyes and looking at the OWUI core code again...

Firstly, your question about latency got me thinking whether my previous response was acceptable.

The "Full Context Mode" setting in Open WebUI is intended to bypass the standard RAG system's context truncation and use the entire document context. However, the way the code is structured, it's not fully bypassing the RAG system. It's augmenting the prompt with the full document context, but still applying a pre-processing step (the RAG template) that it shouldn't be.

The root cause is in open_webui/backend/router/chat.py

The key issue is within the generate_chat_completion function. Even when "Full Context Mode" is enabled, the code still preprocesses the request using RAG logic and inserts a RAG template into the system prompt, which isn't what you want for a custom pipe. It shouldn't be doing any RAG processing if a custom pipe is involved.

Look at this snippet from generate_chat_completion:

async def generate_chat_completion(
    request: Request,
    form_data: dict,
    user: Any,
    bypass_filter: bool = False,
):
   #...
    if model.get("pipe"):
        # Below does not require bypass_filter because this is the only route the uses this function and it is already bypassing the filter
        return await generate_function_chat_completion(
            request, form_data, user=user, models=models
        )



Upvote
2

Downvote

Reply

Award

Share

u/Professional_Ice2017 avatar
Professional_Ice2017
OP
•
7mo ago
This code is saying:

- If a model.get("pipe") exists, route to a generate_function_chat_completion function.

This routes to your custom pipe. But, it doesn't bypass the previous processing steps that inject the RAG system prompt.

The relevant configuration settings (in open_webui/config.py) are:

RAG_FULL_CONTEXT: This is the "Full Context Mode" toggle. When True, it should mean "use the entire document, don't chunk/filter it."

RAG_TEMPLATE: This is the system prompt template used for RAG. It's the string my pipe is seeing: "Respond to the user query using the provided context, incorporating inline citations in the format ..."

So the flow of events (and the bug, IMO) is:

User Input: The user types something into the chat input.

Middleware (in open_webui/backend/middleware.py):

The request goes through middleware, specifically process_chat_payload.

process_chat_payload is where the RAG logic is always applied, regardless of whether a custom pipe is being used.

It checks for features.web_search, features.image_generation, and features.code_interpreter to see if those should be enabled.

Crucially, it always calls get_sources_from_files if there are any files. This function is the heart of the RAG system.

The RAG template (RAG_TEMPLATE) is always prepended to the first user message, or a system prompt is added if one doesn't exist.

get_sources_from_files (in open_webui/backend/retrieval/main.py):



Upvote
2

Downvote

Reply

Award

Share

u/Professional_Ice2017 avatar
Professional_Ice2017
OP
•
7mo ago
This function is responsible for handling document retrieval.

It checks RAG_FULL_CONTEXT. If True, and a document is present, it retrieves the entire document content, using the content key from document.data. This avoids the chunking/embedding/vector search process. This part is working correctly.

If RAG_FULL_CONTEXT is False, or there is no content, this goes through the full vector database query process (using query_collection or query_doc), which is not what you want for a custom pipe.

Even with RAG_FULL_CONTEXT on, the prompt_template function (in open_webui/utils/task.py) always inserts the RAG_TEMPLATE into the system prompt (or prepends it to the first user message), wrapping the retrieved context. This is the core of the problem.

generate_function_chat_completion: The request, now including the modified, RAG-templated prompt, finally goes to your custom pipe. Your pipe receives this unwanted RAG prompt.

The problem is that the RAG system is always invoked and modifies the prompt before the request reaches your custom pipe. The RAG_FULL_CONTEXT flag only controls how much of the document context is retrieved, not whether the RAG system is used at all. It's still doing a retrieval (of the whole document) and using the RAG template.

The workaround I outlined in my blog post is that inside your custom pipe's pipe function, you can detect and remove the RAG template.

This is a brittle workaround. If the RAG_TEMPLATE changes, this code will break. It also means that the full document content will be passed to the pipe even if you don't need it.

"Full Context Mode" should mean "use the full document instead of chunked retrieval," but it shouldn't mean "apply the RAG system prompt and use the RAG system to provide the full document content" The current code is inconsistent with that expectation.

Also worth pointing out is if you want the "Full Document" is binary / base64 format (particularly important to retain data structure in PDFs with text and images and you want to sent it off somewhere for processing), then the "Full Content Mode" setting in OWUI doesn't achieve that. I guess it's wording is accurate.. "full CONTENT", not "full FILE".

I just tested this, with Full Content Mode turned on, and attaching a 4MB PDF file to my prompt... and yeh, I hit a latency problem because OWUI inserted the entire CONTENT into the RAG prompt, which my pipe then had to simply ignore as I wanted to retrieve the entire BINARY file from storage.

If you do indeed want the full CONTENT of a file, then this new OWUI setting (Full Content Mode) is great and you don't even have to bother getting the full content as the OWUI RAG pipeline forcefully injects it into your pipe logic anyway.

It all depends on use-case as to whether the way OWUI handles the storage and retrieval of file is acceptable / workable into your custom pipe / solution or not.
