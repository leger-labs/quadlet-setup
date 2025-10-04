KEY repositories to analyze for the letta implementation:
- https://github.com/wsargent/recipellm
- https://github.com/wsargent/letta-openai-proxy/tree/main

---

Relevant blog post by the same author:
Managing Local LLMs
20 Feb 2025 • llm
This post starts off by talking about getting easier access to logs for diagnosing problems in LLMs, and then there's a second cooking attempt.

After successfully cooking with LLMs, I dug more into the bits that didn't work, and started to get a better appreciation for the limits and complexities of running LLMs locally.

To recap: I've got two physical machines that make up the LLM: the Windows desktop with a Radeon 7800 XT (16GB VRAM), and the devserver in the basement, with 64GB RAM. I run VirtualBox VMs on the devserver as kind of a homegrown Proxmox, so there are VMs that run Open WebUI, Letta, and PostgreSQL with pgvector, all directly accessible on the network through Tailscale.

So this means that when I'm in the kitchen talking to the iPad, it's going through Open WebUI, to Letta, which is then talking to the database and the Windows Desktop with Ollama.

iPad
Open WebUI VM
Letta VM
Database VM
Windows Desktop
Pretty much everything in this chain can and has broken. When it does, the only way I know is that there's a spinning wheel and no output from the other side. In order to figure out what was going wrong, I needed observability.

Getting Things Seen
My first thought was to stick fluentbit on everything and send it to VictoriaLogs, but that didn't work so well – first Fluentbit on Windows didn't like Tailscale DNS at all, and then once I hardcoded it and sorted out the Host HTTP header addressing, VictoriaLogs simply returned 400 Bad Request and refused to tell me why. My attempts to get the otel auto-instrumentation to magically send everything through OTLP likewise died. I'll spare you the gory details, but the short version is that Open WebUI depends on grpc libraries that are in the direct chain for opentelemetry instrumentation, which sticks me with 1.27.0 – older than the zero-code logging. I could get metrics and traces into TelemetryHub, but not logs.

I had vague ideas of scraping journald logs out using the otel collector and doing some post processing, but the JSON serialization was appalling.

And this didn't even touch on Ollama's server.log, containing four or five different log formats in server.log: GIN, some llama-server output, and a couple of other unidentifible things.

Then I realized I'd made a fundamental error: I was reaching for too much gun. I didn't have to care about structured logging, or a unified pipeline, or even getting metrics and distributed tracing in. I just needed to hoover up the logs, in whatever format they came in.

I found Papertrail which was exactly what I needed – step by step instructions on setting up logs in a variety of formats, including Windows (although their link for nxlog is broken, this is the correct link) and even Docker – logspout is great. Between their instructions and the free tier at 16GB a month and web based streaming live logs, I could easily flip between systems and see which one had broken and why.

Getting Things Working
Open WebUI failures were mostly due to configuration errors on my part.

When I set RAG_EMBEDDING_MODEL_AUTO_UPDATE=false and RAG_RERANKING_MODEL_AUTO_UPDATE=false, I thought I was disabling documents, but attachments and document upload uses the same underlying system. I needed to re-enable that and then I needed to switch my embedding model for it to pick up changes.
Open WebUI would hang for a minute if any of the backend connections was down – I didn't make the connection until I realized it only happened when I'd turned the Windows desktop off.
It would triple the amount of work for the model by asking it to fill out the title and tags. I switched it to qwen2.5-0.5b.
Search failures seem to be a combination of two things: backend failures where Kagi didn't like how often I was calling, or internal failures (both of them caused stacktraces instead of known failure conditions). I didn't really deal with this, I just added Tavily to Letta through the Composio integration.
Letta failures were mostly on their end:

Their letta-free LLM uses OpenAI under the hood, and every so often OpenAI will return a 'Internal server error (unpack): 400 Client Error: Bad Request for url: https://api.openai.com/v1/chat/completions' failure. Not much to do except not use that model.
I paid Anthropic $20 for API usage. I've gone through $11.11 so far, so not bad all things considered. When I added the key to Letta, it wouldn't let me select it. I eventually figured out that Anthropic is very strict about API key usage, and I had to create a new API key for Letta – I couldn't just reuse the one for Open WebUI.
There are times when the model looks something up from memory, but does not request a callback: request_heartbeat: false. This means that there's no send_message, and it looks like no response to Open WebUI. It should be fixed in later versions, but I also added "When searching memories or processing information, I first perform the action, then immediately inform users about what I'm doing, ensuring both accurate and transparent communication." to the system prompt so that at the very least it tells me when it's calling a tool.
There were a couple of things I needed to do for Ollama:

I needed to preload the model by sending it an empty request.
I needed to set OLLAMA_KEEP_ALIVE=-1 to keep the model in memory.
Once I fixed all of this (or at least had workarounds), it was time to try cooking again.

Getting Things Cooked
This time it was Spicy Salmon Roll Bowl. This partly because it's another simple recipe, and partly because there is still So Much Rice.

First up, Letta makes it really easy to start off, because it's easy to save stuff in between context windows. No prompt fiddling or copy/paste required: I just asked it "Can you bring up the spicy salmon bowl recipe from your archives?" and it was ready to go.

Here's the Spicy Salmon Roll Bowl recipe, Will! It serves 4 and takes about 40 minutes to make:

Ingredients:

12 oz. salmon fillet (preferably skin-on, cut into 1" cubes)
2 cups sushi rice or other short-grain rice
3 Persian cucumbers, thinly sliced
2 avocados, thinly sliced
3 scallions, thinly sliced
¼ cup unseasoned rice vinegar, plus more for drizzling
3 Tbsp. chili crisp
⅓ cup plus 3 Tbsp. mayonnaise
Pinch of cayenne pepper
Kosher salt
Furikake, shichimi togarashi, and/or toasted sesame seeds for serving
Directions:

Toss cucumbers, vinegar, and salt in a bowl; let them sit
Cook rice with water and salt; fluff when done
Mix chili crisp, vinegar, and mayo for spicy mayo
Broil salmon coated with mayo and cayenne until opaque
Serve rice topped with salmon, cucumbers, avocados, spicy mayo, and scallions
Would you like me to create a mermaid diagram showing the workflow? There are some steps we can do in parallel to make this more efficient!

I was really impressed by what the LLM was able to do. For example, it was able to walk me through what to do when the mayonnaise jar was empty. (Later, I found out I'd left it running on Claude Sonnet, I don't know if the local LLM could have done this.)

No worries, Will! We have a few options here:

If you have Japanese Kewpie mayonnaise, that would actually be perfect for this dish
If you have plain yogurt, we can make a yogurt-based spicy sauce instead
If you have sour cream, we could make a creamy spicy sauce with that
Or we could make a simpler sauce just using the chili crisp with a bit of rice vinegar and a touch of sesame oil if you have it
What ingredients do you have available? Let me know and I'll help you make a delicious alternative sauce!

I had sriracha mayo.

Perfect! Sriracha mayo will work great! Since it's already spicy, we'll modify our sauce recipe:

Mix together:

⅓ cup plus 3 Tbsp. Sriracha mayo
1-2 Tbsp. chili crisp (start with less since the mayo is already spicy)
A splash of rice vinegar
Give it a taste - the Sriracha mayo might actually make it even better than the original recipe! You can adjust by:

Adding more chili crisp if you want more heat and crunch
Adding a bit more vinegar if you want it tangier
How's that taste?

And how many tablespoons 1/3 a cup was:

1/3 cup equals 5 tablespoons plus 1 teaspoon. So for our recipe you'll need:

5 tablespoons + 1 teaspoon (that's the ⅓ cup)
Plus 3 more tablespoons Total: 8 tablespoons + 1 teaspoon of Sriracha mayo
Pro tip: If you're not sure about the exact measurements here, it's okay! Sauce making can be flexible - start with 7 tablespoons and add more to taste. You can always add more, but you can't take it away!

Problem: it wanted me to turn the broiler on and then cook the salmon.

The broiler heats up quickly! You only need to:

Turn it on high
Let it preheat for 3-5 minutes
Position your oven rack about 6 inches from the top heating element
We have a bizarre hand-me-down prosumer oven that the manufacturer refuses to believe exists (we have to prove it to them every time we call) and it doesn't have heating elements at the top. And it takes 20 minutes to preheat. I had told it about oven cooking times, but I was unclear on how broilers typically work and the LLM didn't catch it.

I told it to make a note and store it to user core memory. This is what it added:

Kitchen Equipment Note: Will's broiler requires 20 minutes to fully preheat, unlike standard broilers that typically heat up in 3-5 minutes. This timing should be accounted for in recipe preparations.

The LLM can be a little salty.

And in the end, we had delicious food.
