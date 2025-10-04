This is my simplified docker-compose.yml file for OpenWebUI and qdrant. You can access qdrant at http://your-ip:6333/dashboard and check the collections created. I like to set the volumes with an absolute path and name the default network, but that is just me. I also use tika for RAG.

services:

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    restart: unless-stopped
    ports:
      - "3000:8080/tcp"
    volumes:
      - /opt/docker/open-webui/data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=<your-ip>:11434
      - VECTOR_DB=qdrant
      - QDRANT_URI=http://qdrant:6333


  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - /opt/docker/open-webui/qdrant:/qdrant/storage

networks:
  default:
    name: open-webui
    driver: bridge

---

Here's the relevant sections of the compose file in my stack:

  open-webui:                                                                                               
    environment:                                                                                            
      QDRANT_URI: http://qdrant:6333                                                                        
      VECTOR_DB: qdrant                                                                                     
                                                                                                            
  qdrant:                                                                                                   
    image: qdrant/qdrant                                                                                    
    volumes:                                                                                                
      - ./volumes/qdrant:/qdrant/storage
track me


Upvote
5

Downvote

Reply

Award

Share

u/Better-Barnacle-1990 avatar
Better-Barnacle-1990
OP
•
5mo ago
Ok thx for your comment. when i set the instance do i need to select the datababase in the OpenwebUI settings? or does it automaticly use the database? so i can ask the LLM to search in my documents.



Upvote
1

Downvote

Reply

Award

Share

kantydir
•
5mo ago
The VECTOR_DB var is what tells OWUI which VDB to use



Upvote
1

Downvote

Reply

Award

Share

u/Better-Barnacle-1990 avatar
Better-Barnacle-1990
OP
•
5mo ago
Yes, just for my understanding, the LLM in OWUI use then automatically my DB to search for data if i ask him in the chat?

---

Here is a link to the two required environment parameters QDRANT_URI and QDRANT_API_KEY. A qdrant database hosted locally on your machine, or in the cloud, should work the same. I've not verified this is the case, but based on the QDRANT_URI name, I assume it can be referencing a local URL too. You can provide the environment variables via command line to the OWUI docker container.
