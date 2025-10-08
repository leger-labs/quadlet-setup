## Service Examples

This section is to show how services within docker compose infra can be used 
directly or programmatically without the Open WebUI interface. The examples 
have been created as *.sh scripts that can be executed via the command line.


### Docling

**PDF document to markdown**

Generates a JSON document with the markdown text included. Changes to the config.json document, located in the same directory, can change how Docling responds. More information on how to configure Docling can be found in the [Advanced usage section](https://github.com/docling-project/docling-serve/blob/main/docs/usage.md) of the [Docling Serve documentation](https://github.com/docling-project/docling-serve/blob/main/docs/README.md).

```sh
curl -X POST "http://localhost:3000/docling/v1alpha/convert/source" \
    -H "Cookie: token=<add-jwt-token>" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -d '{ \
      "options": { \
        "do_picture_description": false, \
        "image_export_mode": "embedded", \
        "images_scale": 2.0, \
        "include_images": false, \
        "return_as_file": false, \
        "to_formats": ["md"] \
      }, \
      "http_sources": [{ "url": "https://arxiv.org/pdf/2408.09869" }] \
    }'
```

### Tika

**Information about the PDF document**

Generates meta data from a provided url. More information can be found via the [Metadata Resource documentation](https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=148639291#TikaServer-MetadataResource)

```sh
curl https://arxiv.org/pdf/2408.09869v5 > 2408.09869v5.pdf
curl http://localhost:3000/tika/meta \
    -H "Cookie: token=<add-jwt-token>" \
    -H "Accept: application/json" -T 2408.09869v5.pdf 
```

**PDF document (url) to HTML**

Generates HTML from a provided url. More information can be found via the [Tika Resource Documentation](https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=148639291#TikaServer-GettheTextofaDocument)

```sh
curl https://arxiv.org/pdf/2408.09869v5 > 2408.09869v5.pdf
curl http://localhost:3000/tika/tika \
    -H "Cookie: token=<add-jwt-token>" \
    -H "Accept: text/html" -T 2408.09869v5.pdf 
```

**PDF document (url) to plain text**

Generates plain text from a provided url. More information can be found via the [Tika Resource Documentation](https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=148639291#TikaServer-GettheTextofaDocument)

```sh
curl https://arxiv.org/pdf/2408.09869v5 > 2408.09869v5.pdf
curl http://localhost:3000/tika/tika \
    -H "Cookie: token=<add-jwt-token>" \
    -H "Accept: text/plain" -T 2408.09869v5.pdf 
```

  docling:
    env_file: env/docling.env
    healthcheck:
      interval: 30s
      retries: 5
      start_period: 10s
      test: wget -qO- http://127.0.0.1:5001/health > /dev/null || exit 1
      timeout: 5s
    image: quay.io/docling-project/docling-serve:latest
    restart: unless-stopped



  mcp:
    command: --config /app/conf/config.json
    depends_on:
      - watchtower
    env_file: env/mcp.env
    healthcheck:
      interval: 30s
      retries: 5
      start_period: 5s
      test: "curl -fsSL http://127.0.0.1:8000/time/get_current_time -H 'Content-Type: application/json' -d '{\"timezone\": \"America/Chicago\"}' | grep -v grep | grep 'timezone' || exit 1"
      timeout: 5s
    image: ghcr.io/open-webui/mcpo:latest
    restart: unless-stopped
    volumes:
      - ./conf/mcp:/app/conf:ro



  postgres:
    depends_on:
      - watchtower
    env_file: env/postgres.env
    healthcheck:
      interval: 30s
      retries: 5
      start_period: 20s
      test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}"]
      timeout: 5s
    image: pgvector/pgvector:pg15
    restart: unless-stopped
    volumes:
      - postgres:/var/lib/postgresql/data

  redis:
    depends_on:
      - watchtower
    env_file: env/redis.env
    healthcheck:
      interval: 30s
      retries: 5
      start_period: 20s
      test: ["CMD-SHELL", "redis-cli ping | grep PONG"]
      timeout: 3s
    image: redis/redis-stack:latest
    restart: unless-stopped

  searxng:
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
      - DAC_OVERRIDE
    cap_drop:
      - ALL
    env_file: env/searxng.env
    depends_on:
      - redis
      - watchtower
    healthcheck:
      interval: 30s
      retries: 5
      start_period: 10s
      test: wget -qO- http://127.0.0.1:8080/ > /dev/null || exit 1
      timeout: 5s
    image: searxng/searxng:2025.5.18-5dff826
    logging:
      driver: "json-file"
      options:
        max-size: "1m"
        max-file: "1"
    restart: unless-stopped
    volumes:
      - searxng:/etc/searxng

  tika:
    env_file: env/tika.env
    healthcheck:
      interval: 30s
      retries: 5
      start_period: 5s
      test: wget -qO- http://127.0.0.1:9998/tika > /dev/null || exit 1
      timeout: 5s
    image: apache/tika:latest-full
    restart: unless-stopped

  watchtower:
    command: --cleanup --debug --interval 300
    env_file: env/watchtower.env
    image: containrrr/watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

volumes:
  postgres:
    external: false
  searxng:
    external: false
