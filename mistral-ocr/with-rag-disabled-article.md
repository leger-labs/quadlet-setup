Running LiteLLM and OpenWebUI on Windows Localhost (With RAG Disabled): A Comprehensive Guide
Yong Sheng TanJuly 8, 20252 Comments
In this guide, I’ll show you how to build a high-performance, self-hosted AI chat system by integrating LiteLLM with OpenWebUI—providing a robust and private alternative to commercial chatbot solutions.

Previously, I published a comprehensive walkthrough titled “Running LiteLLM and OpenWebUI on Windows Localhost“, which also featured RAG support using Gemini’s text-embedding-004 and Apache Tika for OCR.

This new guide focuses on two major improvements:

Mistral OCR for document extraction
Mistral OCR offers significantly better results than Apache Tika, especially on documents with complex layouts such as tables, multi-column scientific papers, and journal articles.
It not only extracts raw text but also retains structural elements like headings, tables, and images, outputting clean, structured Markdown or JSON.
Performance Boost by Removing Embedding API Calls
By eliminating the slow, per-request embedding calls to Gemini’s text-embedding-004 (used to convert documents into LLM-ready vectors), latency is greatly reduced and system responsiveness improves. For example, For example, web search times dropped significantly – from 1.5-2.0 minutes with RAG enabled to just around 30 seconds after disabling it.
Additionally, using long-context models such as Gemini 2.0 Flash, 2.5 Flash, or 2.5 Pro – with context windows up to 1 million tokens – can greatly reduce the reliance on RAG altogether.
Prerequisites
Before getting started, make sure the following are installed or available:

Windows Subsystem for Linux (WSL): Enables Linux compatibility on Windows.
Docker Desktop: Required for running containerized applications.
Google AI Studio API Keys (x2): Using free API keys from two separate Google AI Studio accounts to send polling requests helps distribute the load and avoid hitting per-key rate or usage limits, for example, Gemini 2.5 flash with requests per day (RPD) of 250.
Mistral OCR API Key: Used for document extraction. A free tier is available, but uploaded documents must not exceed 50 MB or 1,000 pages.
Tavily Search API Key: Provides fast, LLM-optimized search capabilities for use in RAG setups like OpenWebUI. Includes 1,000 free search queries per month.
Understanding the Components
Our stack consists of several key components:

LiteLLM Proxy – A middleware that standardizes access to various AI models (OpenAI, Gemini, Mistral, etc).
OpenWebUI – A web interface for interacting with AI models.
Two PostgreSQL Databases – Stores configuration and conversation history for OpenWebUI and LiteLLM respectively.
Redis – uses its built‑in Pub/Sub system for WebSocket message brokering in Open WebUI, publishing user events to Redis channels and subscribing across instances so all connected clients receive live, synchronized updates.
Step 1: Create the Folder Structure
Folder structure:

docker-compose.yml – Defines our container services
litellm-config.yaml – Configures LiteLLM and defines models
.env – Stores environment variables and API keys
project
  |-- docker-compose.yml
  |-- litellm-config.yaml
  |-- .env

Step 2: Set Up Docker Network and Volumes
Open a command prompt or PowerShell and execute:

> docker network create proxy

This is to setup the network that will be used for docker-compose.yml later.

Step 3: Configure Your Files
1. docker-compose.yml
This file defines all the services that will run in our environment. The provided configuration sets up:

LiteLLM proxy service with PostgreSQL database.
OpenWebUI service with document processing capabilities, enabled via Mistral OCR.
Two PostgreSQL databases which stores configuration and conversation history for OpenWebUI and LiteLLM respectively.
Redis which enables WebSocket message handling in OpenWebUI using Pub/Sub for real-time client updates.
File location: docker-compose.yml

services:
  # openwebui app
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: openwebui
    depends_on:
      - webui-redis
      - webui-postgres
    volumes:
      - ./data/open-webui:/app/backend/data
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      OPENAI_API_BASE_URLS: ${OPENAI_API_BASE_URLS}
      OPENAI_API_KEYS: ${OPENAI_API_KEYS}
      ENABLE_LITELLM: True
      LITELLM_PROXY_PORT: 4000
      LITELLM_PROXY_HOST: 127.0.0.1
      CORS_ALLOW_ORIGIN: "*" # This is the current Default, will need to change before going live
      # this makes sure that users don't lose login after stack restart
      WEBUI_SECRET_KEY: ${WEBUI_SECRET_KEY}
      # RAG_WEB_SEARCH_TRUST_ENV: True
      GLOBAL_LOG_LEVEL: DEBUG
      DEFAULT_USER_ROLE: pending
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@${POSTGRES_HOST:-webui-postgres}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-postgres}
      DATA_DIR: /app/backend/data
      # OLLAMA_BASE_URLS: http://ollama:11434
      PGVECTOR_DB_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@${POSTGRES_HOST:-webui-postgres}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-postgres}
      VECTOR_DB: ${VECTOR_DB:-pgvector}
      SOCKET_LOG_LEVEL: DEBUG
      # asynchronous chat, notifications, and real-time updates, which is helpful for long-running agents
      ENABLE_WEBSOCKET_SUPPORT: true
      WEBSOCKET_MANAGER: ${WEBSOCKET_MANAGER:-redis}
      WEBSOCKET_REDIS_URL: ${WEBSOCKET_REDIS_URL:-redis://webui-redis:6379/1}
    env_file: .env
    ports:
      - 3000:8080
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped
    networks:
      - internal

  # postgres with pgvector
  webui-postgres:
    image: ankane/pgvector
    container_name: webui-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-postgres}
      POSTGRES_HOST: ${POSTGRES_HOST:-webui-postgres}
      POSTGRES_PORT: ${POSTGRES_PORT:-5432}
    volumes:
      - /opt/open-webui-stack/postgres_data/:/var/lib/postgresql/data
    ports:
      - "5432:${POSTGRES_PORT:-5432}"
    restart: unless-stopped
    networks:
      - internal

  # Redis websocket for OpenWebUI
  webui-redis:
    image: docker.io/valkey/valkey:8.0.1-alpine
    container_name: webui-redis
    ports:
      - "7000:6379"
    volumes:
      - redis-data:/data
    command: "valkey-server --save 30 1"
    healthcheck:
      test: "[ $$(valkey-cli ping) = 'PONG' ]"
      start_period: 5s
      interval: 1s
      timeout: 3s
      retries: 5
    restart: unless-stopped
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
      - DAC_OVERRIDE
    logging:
      driver: "json-file"
      options:
        max-size: "1m"
        max-file: "1"
    networks:
      - internal

  # LiteLLM app
  litellm:
    container_name: litellm
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - 4000:4000 # Map the container port to the host, change the host port if necessary
    volumes:
      - ./litellm-config.yaml:/app/config.yaml # Mount the local configuration file
    # You can change the port or number of workers as per your requirements or pass any new supported CLI augument. Make sure the port passed here matches with the container port defined above in `ports` value
    command: [ "--config", "/app/config.yaml", "--port", "4000", "--num_workers", "8" ]

    environment:
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY:-sk-1234}
      - DATABASE_URL=postgresql://${LITELLM_POSTGRES_USER:-postgres}:${LITELLM_POSTGRES_PASSWORD:-postgres}@${LITELLM_POSTGRES_HOST:-litellm_db}:${LITELLM_POSTGRES_PORT:-5432}/${LITELLM_POSTGRES_DB:-postgres}
      - STORE_MODEL_IN_DB=True # allows adding models to proxy via UI
      - UI_USERNAME=${UI_USERNAME}
      - UI_PASSWORD=${UI_PASSWORD}
    env_file:
      - .env
    depends_on:
      - litellm_db
    networks:
      - internal
  
  # LiteLLM database
  litellm_db:
    image: postgres:16.1
    container_name: litellm_db
    restart: always
    ports:
      - "5433:${LITELLM_POSTGRES_PORT:-5432}"
    environment:
      - POSTGRES_USER=${LITELLM_POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${LITELLM_POSTGRES_PASSWORD:-postgres}
      - POSTGRES_PORT=${LITELLM_POSTGRES_PORT:-5432}
      - POSTGRES_DB=${LITELLM_POSTGRES_DB:-postgres}
      - POSTGRES_HOST=${LITELLM_POSTGRES_HOST:-litellm_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal


volumes:
  redis-data:
  postgres_data:

networks:
  proxy:
    external: true

  internal:
    driver: bridge

2. litellm-config.yaml
This file contains the configuration for the Gemini models you want to access through LiteLLM. The provided configuration is as follows:

File location: litellm-config.yaml

model_list:
    # GEMINI : https://aistudio.google.com/apikey
    - model_name: gemini/*
      litellm_params:
        model: gemini/*
        api_key: os.environ/GEMINI_API_KEY1
        rpm: 15
        tpm: 1000000
        drop_params: true # Just drop_params when calling specific models
        modify_params: true # to solve the problem with cline plugin in vscode
    - model_name: gemini/*
      litellm_params:
        model: gemini/*
        api_key: os.environ/GEMINI_API_KEY2
        rpm: 15
        tpm: 1000000
        drop_params: true # Just drop_params when calling specific models
        modify_params: true # to solve the problem with cline plugin in vscode

general_settings:
    forward_openai_org_id: true

litellm_settings:
    enable_json_schema_validation: True

Source: LiteLLM’s documentation

3. .env
The environment file stores all sensitive information and configuration settings, including:

OpenWebUI settings and connection details
LiteLLM authentication details
Gemini API Keys from two different Google AI studio accounts for polling requests
Web search integration options, powered by Tavily AI
File location: .env

(Note: please remember to edit the .env file to add web search capabilities such as Tavily AI. At minimum, you need to add Gemini API Keys. Also, remember to change sk-1234 for your LiteLLM’s API key; remember to change WEBUI_SECRET_KEY and MISTRAL_OCR_API_KEY)

# 1. openwebui
OPENAI_API_BASE_URLS=http://litellm:4000/v1
OPENAI_API_KEYS=sk-1234
WEBUI_SECRET_KEY=<YOUR_WEBUI_SECRET_KEY>

## Bypass embedding for OpenWebUI
BYPASS_EMBEDDING_AND_RETRIEVAL=True

## Vector database
VECTOR_DB=pgvector
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_HOST=webui-postgres
POSTGRES_PORT=5432

## Content Extraction Engine
CONTENT_EXTRACTION_ENGINE=mistral_ocr
MISTRAL_OCR_API_KEY=<YOUR_MISTRAL_OCR_API_KEY>

## Websocket setup
WEBSOCKET_MANAGER=redis
WEBSOCKET_REDIS_URL=redis://webui-redis:6379/1

## Web Search
ENABLE_WEB_SEARCH=True
ENABLE_SEARCH_QUERY_GENERATION=True
BYPASS_WEB_SEARCH_EMBEDDING_AND_RETRIEVAL=True
WEB_SEARCH_RESULT_COUNT=15
WEB_SEARCH_CONCURRENT_REQUESTS=2
WEB_SEARCH_ENGINE=tavily
TAVILY_API_KEY=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
WEB_LOADER_ENGINE=tavily
TAVILY_EXTRACT_DEPTH=basic

## Disable ollama
ENABLE_OLLAMA_API=False

# 2. LiteLLM
LITELLM_MASTER_KEY=sk-1234 # can change, but need to same as OPENAI_API_KEYS environment variable
LITELLM_API_BASE=http://litellm:4000
UI_USERNAME=<YOUR_LITELLM_UI_USERNAME>
UI_PASSWORD=<YOUR_LITELLM_UI_PASSWORD>

## database
LITELLM_POSTGRES_USER=postgres
LITELLM_POSTGRES_PASSWORD=postgres
LITELLM_POSTGRES_DB=postgres
LITELLM_POSTGRES_HOST=litellm_db
LITELLM_POSTGRES_PORT=5432

## LLM API Key
GEMINI_API_KEY1=<YOUR_GEMINI_API_KEY>
GEMINI_API_KEY2=<YOUR_GEMINI_API_KEY>

Source: OpenWebUI’s environment configuration

Step 4: Launch the Services
From your project directory, run:

docker compose up -d

This command starts all the services in detached mode. The first run will take some time as it downloads the necessary Docker images.

Starting all the services may take a while. In the meantime, you can use the following command to monitor their status:

docker compose logs -f

Step 5: Access Your OpenWebUI
Once all services are running, open your browser and navigate to http://localhost:3000 to access OpenWebUI.


Then, you could select gemini/gemini-2.5-flash, and turn on ‘Web Search’ function.


You could also upload a pdf, and then ask question about the book.


Another feature I personally love in OpenWebUI to use is “Knowledge base”, as I could store the documents file relevant to a topic amd perform an QnA for that knowledge base.


Here are some examples of the knowledge (in PDF format) I’ve uploaded to the knowledge base.


And I can ask questions about any PDF file in the knowledge base, or about the entire collection.



Bonus 1: Setup Thinking Mode for Gemini
Some Gemini models, such as gemini-2.5-flash and gemini-2.5-pro, include both “thinking” and “non-thinking” variants. When accessed via API, the non-thinking mode is used by default.

To set thinking mode for gemini-2.5-flash, click “User Profile” icon at bottom left >> “Admin Panel” button >>“Settings” >> “Models”, and then select the gemini-2.5-flash.


Then navigate to “Advanced Params”, then change the ‘Reasoning Effort” parameter to either “low”, “medium”, or “high” based on your needs. After done, remember to click “Save & Update” button at the bottom to save this settings.


Go back to the chat UI again, and type your query there. You will see that the thinking mode is now enabled for gemini-2.5-flash model.


Bonus 2: Setup Google Search in Gemini API
This step is optional and only applies to Gemini models—use it if you prefer Google Search instead of Tavily AI Search.

Go back to the gemini-2.5-flash model settings you configured in Bonus 1. Click on ‘Advanced Params’, then select ‘+ Add Custom Parameter’. Add a key-value pair with tools as the key and [{"googleSearch": {}}] as the value. Once done, make sure to click the ‘Save & Update’ button at the bottom to apply the changes.


Go back to the chat UI again, and type your query there which let AI to help you to search latest info, for example, “what is happening in Malaysia”. You will see how Gemini models search the recent news about Malaysia.



Bonus 3: Setup URL context in Gemini API
This step is optional and only applies to Gemini models – enable it if you want the model to fetch and analyze content directly from your provided URLs to inform and enrich its response

Go back to the gemini-2.5-flash model settings you configured in Bonus 1. Click on ‘Advanced Params’, then select ‘+ Add Custom Parameter’. Add a key-value pair with tools as the key and [{"urlContext": {}}] as the value. Once done, make sure to click the ‘Save & Update’ button at the bottom to apply the changes.


Go back to the chat UI again, and type your query there with URL provided, for example: “Summarize this article: <web page url>”. You will see the


Bonus 4: Monitoring LLM usage via LiteLLM
Also, if you want to monitor your LLM usage in LiteLLM, you could login to http://localhost:4000/ui, and then login using the username and password you set on UI_USERNAME and UI_PASSWORD.

You could also check what are the LLM models are successfully added to LiteLLM here:

Also, you could monitor the LLM logs here:

Related posts:
