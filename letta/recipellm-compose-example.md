# RecipeLLM

This is an "out of the box" system that sets up an AI agent with a recipe manager and a notification system.


## Why Use It?

I started working on this a few months ago to learn how to cook.  It's like working with an experienced chef that can answer questions and fill in the gaps on cooking.

The first time you start it, you go to http://localhost:3000 to use [Open WebUI](https://docs.openwebui.com/) and start filling the agent in on your skill level and what you want.  It will remember your details and can adjust recipes and instructions to match your personal tastes.

![introduction](./introduction.png)

It can search the web and [import recipes into Mealie](https://tersesystems.com/blog/2025/03/01/integrating-letta-with-a-recipe-manager/), but it's also good at describing the recipe in context:

![cooking](./cooking.png)

When you start cooking, you can tell it what you're doing and it will walk you through any adjustments you need to make and let you know how to fix any mistakes.  For example, you can unpack the prep work into actual instructions:

![prep work](./prep_work.png)

I like to use this while I'm on the iPad, using Apple Dictation.  The below picture shows me using the self-hosted dev environment while making [ginger chicken](https://tersesystems.com/blog/2025/03/07/llm-complexity-and-pricing/).

![ipad](https://tersesystems.com/images/2025-03-07/letta.jpg)

## Requirements

You will need [Docker Compose](https://docs.docker.com/compose/install/) installed.

RecipeLLM requires an API key to a reasonably powerful LLM: either OpenAI, Anthropic, or Gemini.  You'll need to set `env.example` to `.env` and set the API and `LETTA_CHAT_MODEL` appropriately.

If you want to use Google AI Gemini models, you will need a [Gemini API key](https://ai.google.dev/gemini-api/docs/api-key).

```
LETTA_CHAT_MODEL=google_ai/gemini-2.5-flash
```

If you want to use Claude Sonnet 4, you'll want an [Anthropic API Key](https://console.anthropic.com/settings/keys).

```
LETTA_CHAT_MODEL=anthropic/claude-sonnet-4-20250514
```

If you want to use OpenAI, you'll want an [OpenAI API Key](https://platform.openai.com/api-keys).

```
LETTA_CHAT_MODEL=openai/gpt-4.1
```

You can also download recipes from the web if you have [Tavily](https://www.tavily.com/) set up.  An API key is free and you can do 1000 searches a month.

## Running

Set up the system by running docker compose

```
docker compose up --build
```

The Docker Compose images may take a while to download and run, so give them a minute.  Once they're up, you'll have three web applications running:

* Open WebUI (how you chat with the agent): [http://localhost:3000](http://localhost:3000)
* ntfy (which handles real time notifications): [http://localhost:80](http://localhost:80)
* Mealie (the recipe manager): [http://localhost:9000](http://localhost:9000)

There's also the OpenAI proxy interface if you want to connect directly to the agent:

* OpenAI API: [http://localhost:1416/v1/models](http://localhost:1416/v1/models)

## Notifications

You can ask it to set reminders and notifications for you -- these will be sent to the local ntfy instance at http://localhost and you will hear a ping when the timer goes off.  You can also configure ntfy to send notifcations to your iPhone or Android device, which is what I do personally.

## Modifications

If you want to debug or add to the chef agent, you can use [Letta Desktop](https://docs.letta.com/guides/desktop/install) and connect to the database using `letta` as the username, password, and database:

```
postgresql://letta:letta@localhost:5432/letta
```

When you connect via Letta Desktop it'll look like this:

![Letta Desktop](./letta_desktop.png)

You can change your model, add more instructions to core memory, and add or remove tools.

## Resetting

To delete the existing data and start from scratch, you can down and delete the volume and orphans:

```
docker compose down -v --remove-orphans
```

services:

  ############################################
  # Mealie
  ############################################  

  mealie:
    image: ghcr.io/mealie-recipes/mealie:latest 
    container_name: recipellm-mealie
    restart: always
    ports:
      - "8080:9001"
      - "9000:9000"
    deploy:
      resources:
        limits:
          memory: 1000M # 
    volumes:
      - mealie-data:/app/data/
      - "/etc/localtime:/etc/localtime:ro"
      - "/etc/timezone:/etc/timezone:ro"
    environment:
      # Set Backend ENV Variables Here
      ALLOW_SIGNUP: "true"      

  ############################################
  # MCP Server
  ############################################
  
  mcp:
    build:
      context: ./mcp
      dockerfile: Dockerfile
    container_name: recipellm-mcp
    volumes:
      - "/etc/localtime:/etc/localtime:ro"
      - "/etc/timezone:/etc/timezone:ro"
      - mcp-data:/app/data
    ports:
      - "8000:8000"
    environment:
      NTFY_SERVER: http://recipellm-ntfy
      MEALIE_BASE_URL: http://recipellm-mealie:9000
      LETTA_BASE_URL: http://recipellm-letta:8283
      RECIPELLM_MCP_SERVER_URL: http://recipellm-mcp:8000/sse/   
      # chat model to use when the chef-agent is created.
      #LETTA_CHAT_MODEL: "anthropic/claude-sonnet-4-20250514"
      LETTA_CHAT_MODEL: $LETTA_CHAT_MODEL
      TAVILY_API_KEY: $TAVILY_API_KEY
    depends_on:
      letta:
        condition: service_healthy
      mealie:
        condition: service_healthy
    restart: on-failure
    command: >
      sh -c "
        /app/.venv/bin/python /app/main.py &
        sleep 10 &&
        curl -X POST http://localhost:8000/setup &&
        wait
      "

  ############################################
  # MCP Server
  ############################################

  # Letta is an agent building framework with built-in memory/vectordb support.
  # https://docs.letta.com/quickstart/docker
  letta:
    image: letta/letta:0.9.0
    container_name: recipellm-letta
    ports:
      - 8283:8283
      - 5432:5432
    #volumes:
      # This lets you see pgdata in the home directory and use it from Letta Desktop
      # It _does_ mean that letta's memory persists even if you use docker compose down -v though
      # This is less reliable for me than just using TCP/IP over port 5432 so I usually don't.
      # - ~/.letta/.persist/pgdata:/var/lib/postgresql/data
    environment:
      LETTA_DEBUG: "${LETTA_DEBUG:-false}"
      # https://docs.letta.com/guides/server/providers/anthropic
      ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY
      # https://docs.letta.com/guides/server/providers/google
      GEMINI_API_KEY: $GEMINI_API_KEY 
      # Setting this up means we can do postgresql://letta:letta@localhost:5432/letta in Letta Desktop
      # https://docs.letta.com/guides/desktop/install
      LETTA_PG_DB: ${LETTA_PG_DB:-letta}
      LETTA_PG_USER: ${LETTA_PG_USER:-letta}
      LETTA_PG_PASSWORD: ${LETTA_PG_PASSWORD:-letta}
      TAVILY_API_KEY: ${TAVILY_API_KEY}
    restart: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:8283/v1/health/"]
      interval: 5s
      timeout: 5s
      retries: 18
      start_period: 1s


  # Open WebUI is the front-end UI to Letta
  open-webui:
    image: ghcr.io/open-webui/open-webui:0.6.18
    container_name: recipellm-open-webui
    volumes:
     - open-webui:/app/backend/data
    ports:
      - 3000:8080
    environment:
      # https://docs.openwebui.com/getting-started/env-configuration/
      - GLOBAL_LOG_LEVEL=INFO
      # Disable admin login
      - WEBUI_AUTH=false
      # Enable the /docs endpoint for OpenAPI viewing
      #- ENV=dev
      # Prevent a langchain warning
      - USER_AGENT=openwebui
      # Set tags and titles explictly
      - ENABLE_TAGS_GENERATION=false
      - ENABLE_TITLE_GENERATION=false
      #- TASK_MODEL=$TASK_MODEL
      #- TASK_MODEL_EXTERNAL=$TASK_MODEL_EXTERNAL
      # Disable some meaningless options
      - ENABLE_EVALUATION_ARENA_MODELS=false
      - ENABLE_AUTOCOMPLETE_GENERATION=false
      - ENABLE_RETRIEVAL_QUERY_GENERATION=false
      - ENABLE_FOLLOW_UP_GENERATION=false
      # OpenAI selection should go to Hayhooks to show agents
      - ENABLE_OPENAI_API=true
      - OPENAI_API_BASE_URL=http://recipellm-letta-openai-proxy:1416
      - OPENAI_API_KEY=no_key_required
      # Ollama Options
      - ENABLE_OLLAMA_API=false
      # RAG options can be transformers, ollama, or openai 
      - RAG_EMBEDDING_ENGINE=openai
      # Tavily Web Search in Open WebUI
      - ENABLE_WEB_SEARCH=false
      - WEB_SEARCH_ENGINE=tavily
      - TAVILY_API_KEY=$TAVILY_API_KEY
      # Audio options
      #- AUDIO_STT_ENGINE=$AUDIO_STT_ENGINE
    restart: unless-stopped
    # https://docs.openwebui.com/getting-started/advanced-topics/monitoring/#basic-health-check-endpoint
    # healthcheck:
    #   test: ["CMD", "curl", "-f", "http://127.0.0.1:3000/health"]
    #   interval: 10s
    #   timeout: 5s
    #   retries: 18
    #   start_period: 5s

  ntfy:
      image: binwiederhier/ntfy:latest
      container_name: recipellm-ntfy
      restart: always
      ports:
        - "80:80"
      volumes:
        - ntfy-cache:/var/cache/ntfy
        - ntfy-data:/var/lib/ntfy
      environment:
        - NTFY_BASE_URL=http://localhost
        - NTFY_CACHE_FILE=/var/cache/ntfy/cache.db
        - NTFY_AUTH_FILE=/var/lib/ntfy/user.db
        - NTFY_BEHIND_PROXY=true
        - NTFY_UPSTREAM_BASE_URL=https://ntfy.sh
      deploy:
        resources:
          limits:
            memory: 512M
      command: serve

  ############################################
  # Letta OpenAI Proxy
  ############################################

  letta-openai-proxy:
    build:
      context: ./openai-proxy
      dockerfile: Dockerfile
    container_name: recipellm-letta-openai-proxy
    restart: always
    ports:
      - "1416:1416"
    environment:
      LETTA_BASE_URL: http://recipellm-letta:8283
      HAYHOOKS_HOST: "0.0.0.0"
      HAYHOOKS_PORT: "1416"
    depends_on:
      letta:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 512M

volumes:
  mealie-data:
  mcp-data:
  ntfy-data:
  ntfy-cache:
  open-webui:

  ---

example .env file
# Example env file -- rename this to .env

# https://app.tavily.com/home
TAVILY_API_KEY=

# https://console.anthropic.com/settings/keys
#ANTHROPIC_API_KEY=

# https://ai.google.dev/gemini-api/docs/api-key
#GEMINI_API_KEY=

# https://platform.openai.com/account/api-keys
#OPENAI_API_KEY=

# chat model to use when the chef-agent is created.
#LETTA_CHAT_MODEL="anthropic/claude-sonnet-4-20250514"
#LETTA_CHAT_MODEL="google_ai/gemini-2.5-flash"
