## Game Platform RAG Chatbot (Docker)

### 1) Configure env
Copy `.env.example` to `.env` and edit if needed.

### 2) Start containers
docker compose up --build -d

### 3) Pull the LLM model into Ollama if not pulled already
docker exec -it rag_ollama ollama pull mistral

(Or change OLLAMA_MODEL in .env.)

### 4) Ingest your knowledge base

This request checks if there are new documents with information (like new rules for a game), and if 
there are, it updates the chroma vector database.

DO THIS ALWAYS AT FIRST RUN, so there is a db

curl -X POST "http://localhost:8000/ingest?reset=true"

### 5) Chat
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query":"How many pieces do I have in chess?"}'
