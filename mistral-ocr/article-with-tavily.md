Running LiteLLM and OpenWebUI on Windows Localhost: A Comprehensive Guide
Yong Sheng TanMarch 15, 20254 Comments
In this guide, I’ll walk you through setting up a powerful local AI environment by combining LiteLLM (for managing multiple AI model providers) with OpenWebUI (for a user-friendly interface). This setup allows you to create a self-hosted alternative to commercial chatbots while maintaining control over your data and API keys.

Prerequisites
Before we begin, ensure you have the following installed:

Windows Subsystem Linux (WSL) – Enables Linux compatibility on Windows
Docker Desktop – For containerizing our applications
Tavily AI – The Tavily Search API is a search engine designed for LLMs and RAG, optimized for fast, efficient, and persistent search results. It will be integrated into OpenWebUI.
Understanding the Components
Our stack consists of several key components:

LiteLLM Proxy – A middleware that standardizes access to various AI models (OpenAI, Gemini, Mistral, etc.)
PostgreSQL Database – Stores configuration and conversation history for LiteLLM
OpenWebUI – A web interface for interacting with AI models
Apache Tika – For document parsing and extraction (enables RAG functionality)
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

LiteLLM proxy service with PostgreSQL database
OpenWebUI service with document processing capabilities
Apache Tika service for document extraction in OpenWebUI
The network configuration ensures proper isolation and communication between services.

File location: docker-compose.yml

services:
  ## Setting up the LiteLLM instances
  litellm:
    container_name: litellm
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - 4000:4000 # Map the container port to the host, change the host port if necessary
    volumes:
      - ./litellm-config.yaml:/app/config.yaml # Mount the local configuration file
    # You can change the port or number of workers as per your requirements or pass any new supported CLI augument. Make sure the port passed here matches with the container port defined above in `ports` value
    command: [ "--config", "/app/config.yaml", "--port", "4000", "--num_workers", "8" ]
    networks:
      - proxy
      - internal
    environment:
      - LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY:-sk-1234}
      - DATABASE_URL=postgresql://${LITELLM_POSTGRES_USER:-postgres}:${LITELLM_POSTGRES_PASSWORD:-postgres}@${LITELLM_POSTGRES_HOST:-litellm_db}:${LITELLM_POSTGRES_PORT:-5432}/${LITELLM_POSTGRES_DATABASE:-postgres}
      - STORE_MODEL_IN_DB=True # allows adding models to proxy via UI
      - UI_USERNAME=${UI_USERNAME}
      - UI_PASSWORD=${UI_PASSWORD}
    env_file:
      - .env
    depends_on:
      - litellm_db

  litellm_db:
    image: postgres:16.1
    container_name: litellm_db
    restart: always
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=${LITELLM_POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${LITELLM_POSTGRES_PASSWORD:-postgres}
      - POSTGRES_PORT=${LITELLM_POSTGRES_PORT:-5432}
      - POSTGRES_DATABASE=${LITELLM_POSTGRES_DATABASE:-postgres}
      - POSTGRES_HOST=${LITELLM_POSTGRES_HOST:-litellm_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal

  ## Setting up for OpenWebUI instance
  openwebui:
    container_name: open-webui
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - 3000:8080
    volumes:
      - open-webui-local:/app/backend/data
      - ./data/docs:/data/docs
    environment:
      - OPENAI_API_BASE_URLS=${OPENAI_API_BASE_URLS}
      - OPENAI_API_KEYS=${OPENAI_API_KEYS}
      - ENABLE_LITELLM=True
      - LITELLM_PROXY_PORT=4000
      - LITELLM_PROXY_HOST=127.0.0.1
      ## apache tika
      - TIKA_SERVER_URL=http://tika:9998
      - CONTENT_EXTRACTION_ENGINE=tika
    env_file:
      - .env
    restart: unless-stopped
    networks:
      - proxy
      - internal

  tika:
    image: apache/tika:latest-full
    container_name: tika
    ports:
      - "9998:9998"
    restart: unless-stopped
    networks:
      - internal

networks:
  proxy:
    external: true
  internal:

volumes:
  postgres_data:
  open-webui-local:

2. litellm-config.yaml
This file contains the configuration for all AI models you want to access through LiteLLM. The provided configuration includes:

Google’s Gemini models
OpenAI models (including DALL-E 3)
GitHub Models (gpt-4o-mini)
AWS Bedrock models
Openrouter (model aggregator)
Cohere models
xAI Grok models
Mistral models
Codestral models
Groq Cloud models
Each model configuration includes settings for rate limits, parameter handling, and API key references.

File location: litellm-config.yaml

model_list:
    # GEMINI : https://aistudio.google.com/apikey
    - model_name: gemini/*
      litellm_params:
        model: gemini/*
        api_key: os.environ/GEMINI_API_KEY
        rpm: 15
        tpm: 1000000
        drop_params: true # Just drop_params when calling specific models
        modify_params: true # to solve the problem with cline plugin in vscode
  
    ## GEMINI's text embedding
    - model_name: gemini/text-embedding-004
      litellm_params:
        model: gemini/text-embedding-004
        api_key: os.environ/GEMINI_API_KEY
        rpm: 15
        tpm: 1000000
        drop_params: true # Just drop_params when calling specific models


    # OpenAI : https://platform.openai.com/api-keys
    - model_name: openai/*
      litellm_params:
        model: openai/*
        api_key: os.environ/OPENAI_API_KEY
        drop_params: true


    # Github Models : https://github.com/marketplace/models
    - model_name: github/gpt-4o-mini
      litellm_params:
        model: github/gpt-4o-mini
        api_key: os.environ/GITHUB_API_KEY
        drop_params: true
  
    # AWS Bedrock : https://aws.amazon.com/bedrock/
    - model_name: bedrock/*
      litellm_params:
        model: bedrock/*
        aws_region_name: os.environ/AWS_REGION_NAME
        aws_access_key_id: os.environ/AWS_ACCESS_KEY_ID
        aws_secret_access_key: os.environ/AWS_SECRET_ACCESS_KEY
        drop_params: true
        modify_params: true
  

    # Openrouter : https://openrouter.ai/settings/keys
    - model_name: openrouter/*
      litellm_params:
        model: openrouter/*
        api_key: os.environ/OPENROUTER_API_KEY


    # Cohere : https://dashboard.cohere.com/api-keys
    - model_name: cohere_chat/*
      litellm_params:
        model: cohere_chat/*
        api_key: os.environ/COHERE_API_KEY
        rpm: 20
        tpm: 1000
        drop_params: true
        modify_params: true
        ## all endpoints are limited to 1k calls per month


     # xAI - grok : https://console.x.ai/
    - model_name: xai/*
      litellm_params:
        model: xai/*
        api_key: os.environ/XAI_API_KEY
        modify_params: true
        drop_params: true

    # MISTRAL LLM MODEL - https://console.mistral.ai/api-keys
    - model_name: mistral/*
      litellm_params:
        model: mistral/*
        api_key: os.environ/MISTRAL_API_KEY
        rpm: 60
        tpm: 500000
        drop_params: true
        # modify_params: true


    # Codestral - https://console.mistral.ai/api-keys
    - model_name: codestral/*
      litellm_params:
        model: codestral/*
        api_key: os.environ/CODESTRAL_API_KEY
        rpm: 30
        drop_params: true


    # GROQ CLOUD : https://console.groq.com/keys
    - model_name: groq/*
      litellm_params:
        model: groq/*
        api_base: https://api.groq.com/openai/v1
        api_key: os.environ/GROQ_API_KEY
        drop_params: True


general_settings:
    forward_openai_org_id: true

litellm_settings:
    enable_json_schema_validation: True

Source: LiteLLM’s documentation

3. .env
The environment file stores all sensitive information and configuration settings, including:

OpenWebUI settings and connection details
Apache Tika configuration
LiteLLM authentication details
Retrieval-Augmented Generation (RAG) settings, utilizing gemini/text-embedding-004 as the embedding model
Web search integration options, powered by Tavily AI
File location: .env

(Note: please remember to edit the .env file and add any model API keys such as Gemini, OpenAI, Mistral, etc., or you could add web search capabilities such as Tavily AI. At minimum, you need to add Gemini API Keys because we set gemini/text-embedding-004 as our embedding model. Also, remember to change sk-1234 for your LiteLLM’s API key)

# 1. Settings for OpenWebUI
OPENAI_API_BASE_URLS=http://litellm:4000
OPENAI_API_KEYS=sk-1234 # can change 

## RAG Embedding
RAG_EMBEDDING_ENGINE=openai
RAG_OPENAI_API_BASE_URL=http://litellm:4000
RAG_OPENAI_API_KEY=sk-1234
RAG_EMBEDDING_MODEL=gemini/text-embedding-004
RAG_EMBEDDING_OPENAI_BATCH_SIZE=100
ENABLE_RETRIEVAL_QUERY_GENERATION=True
ENABLE_RAG_HYBRID_SEARCH=false
RAG_TOP_K=10
CHUNK_SIZE=2000
CHUNK_OVERLAP=200
PDF_EXTRACT_IMAGES=True
RAG_FILE_MAX_SIZE=300
## Web Search
ENABLE_RAG_WEB_SEARCH=True
ENABLE_SEARCH_QUERY_GENERATION=True
RAG_WEB_SEARCH_RESULT_COUNT=15
RAG_WEB_SEARCH_CONCURRENT_REQUESTS=3
RAG_WEB_SEARCH_ENGINE=tavily
TAVILY_API_KEY=<YOUR_TAVILY_API_KEY>
## Disable ollama
ENABLE_OLLAMA_API=False

# 2. Setting for LiteLLM
LITELLM_MASTER_KEY=sk-1234 # can change, but need to same as OPENAI_API_KEYS environment variable
LITELLM_API_BASE=http://litellm:4000
UI_USERNAME=<YOUR_LITELLM_UI_USERNAME>
UI_PASSWORD=<YOUR_LITELLM_UI_PASSWORD>

## LLM API
# Note: must fill gemini_api_key because I set the gemini/text-embedding-004 as our default embedding model
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
OPENAI_API_KEY=
GITHUB_API_KEY=
OPENROUTER_API_KEY=
COHERE_API_KEY=
MISTRAL_API_KEY=
CODESTRAL_API_KEY=
GROQ_API_KEY=
XAI_API_KEY=
### AWS Bedrock
CUSTOM_AWS_REGION_NAME=
CUSTOM_AWS_ACCESS_KEY_ID=
CUSTOM_AWS_SECRET_ACCESS_KEY=

Source: OpenWebUI’s environment configuration

Step 4: Launch the Services
From your project directory, run:

docker compose up -d

This command starts all the services in detached mode. The first run will take some time as it downloads the necessary Docker images.

Starting all the services may take a while. In the meantime, you can use the following command to monitor their status:

docker compose logs -f

Step 5: Access Your OpenWebUI
Once all services are running:

Open your browser and navigate to http://localhost:3000 to access OpenWebUI.

Then, you could select gemini/gemini-2.0-flash, and turn on ‘Web Search’ function.

You could also upload a pdf, and then ask question about the book.

Additional Note to OpenWebUI’s web search settings
If your LLM has a long context window (like Gemini), you can bypass embedding and retrieval in the Web Search settings. This prevents search results from being indexed in the vector database and instead feeds them directly into the LLM’s context window, potentially improving chat speed.


Some users might prefer this approach for better search results, but personally, I don’t like it. The reason is that if I enable it, I lose the flexibility to switch to models with smaller context windows easily.

Bonus: Monitoring LLM usage via LiteLLM
Also, if you want to monitor your LLM usage in LiteLLM, you could login to http://localhost:4000/ui, and then login using the username and password you set on UI_USERNAME and UI_PASSWORD.

You could also check what are the LLM models are successfully added to LiteLLM here:

Also, you could monitor the LLM logs here:
