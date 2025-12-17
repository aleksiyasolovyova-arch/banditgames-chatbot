# Game Platform RAG Chatbot (Docker)

This project implements a **Retrieval-Augmented Generation (RAG) chatbot** designed to support a multi-game platform.
The chatbot can explain **game rules**, **strategies**, and **platform usage**, using a vector database and a local LLM.

The system is fully containerised using **Docker**, supports **live knowledge base updates**, and guarantees that the vector database is always available at runtime.

---

## Architecture Overview

The system consists of the following main components:

* **FastAPI backend** – exposes REST endpoints for chat and ingestion
* **ChromaDB** – persistent vector database for embeddings
* **Hugging Face sentence-transformer** – text embedding model
* **Ollama** – local LLM runtime
* **Redis** – response caching
* **Docker Compose** – orchestration and persistence

The chatbot uses **Retrieval-Augmented Generation (RAG)**:

1. User query is converted into an embedding
2. Relevant document chunks are retrieved from ChromaDB
3. Retrieved context is injected into an LLM prompt
4. The LLM generates a grounded response

---

## 1) Environment Configuration

Copy the example environment file and adjust values if needed:

```
cp .env.example .env
```

Key environment variables:

* `EMBED_MODEL` – Hugging Face embedding model
* `OLLAMA_MODEL` – LLM used by Ollama
* `CHROMA_PATH` – persistent vector database location
* `TOP_K` – number of document chunks retrieved per query

---

## 2) Start Containers

Build and start all services:

```
docker compose up --build -d
```

Note: The first build may take several minutes due to machine learning dependencies such as PyTorch.

---

## 3) Pull the LLM Model into Ollama (Once)

If the model has not been pulled previously:

```
docker exec -it rag_ollama ollama pull mistral
```

You only need to do this **once per model**, as models are persisted in a Docker volume.

---

## 4) Knowledge Base Ingestion (Core Concept)

### 4.1 Automatic Startup Ingestion

On application startup, the system runs a **bootstrap process** using FastAPI lifespan events.

This process:

1. Connects to ChromaDB
2. Checks whether a vector collection already exists
3. If embeddings are found, no action is taken
4. If the database is empty, all files in the `data/` directory are ingested

This guarantees:

* The chatbot never starts with an empty vector database
* Persistent data is not re-ingested unnecessarily
* Startup behaviour is idempotent and safe

---

### 4.2 Ingest Endpoint (Live Updates)

The platform supports **live updates** to the knowledge base while the system is running.

Supported document formats:

* Markdown (`.md`)
* PDF (`.pdf`)
* Plain text (`.txt`)

#### Ingestion Flow

1. Documents are loaded from the `data/` directory
2. Text is split into semantically meaningful chunks
3. Each chunk is embedded using a Hugging Face model
4. Embeddings are stored in ChromaDB with stable chunk IDs
5. The database is persisted immediately

---

### 4.3 Manual Ingestion API
If you put a new document in the data folder, it needs to be ingested.

To trigger ingestion manually:

```
curl -X POST "http://localhost:8000/ingest"
```

This will:

* Add new documents
* Update embeddings for modified files
* Leave existing data intact

---

### 4.4 Full Reindex (Reset)

To completely rebuild the vector database:

```
curl -X POST "http://localhost:8000/ingest?reset=true"
```

This will:

* Clear the existing ChromaDB collection
* Re-ingest all documents from the `data/` directory

Use this option when a full reindex is required.

---

### 4.5 Recommended Workflow

| Situation          | Action                |
| ------------------ | --------------------- |
| First startup      | Automatic ingestion   |
| Add new rules      | Add file → `/ingest`  |
| Edit rules         | Edit file → `/ingest` |
| Major restructure  | `/ingest?reset=true`  |
| Restart containers | No action needed      |

---

## 5) Chat with the System

Send a query to the chatbot:

```
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query":"How many pieces do I have in chess?"}'
```

The chatbot will:

1. Retrieve relevant document chunks
2. Generate a grounded response
3. Cache the response for faster repeated queries

---

## 6) Persistence and Safety

* ChromaDB data is stored in a Docker volume
* LLM models are stored in a Docker volume
* Sensitive configuration is excluded via `.gitignore`
* The system is safe to restart without data loss

---

## 7) Design Rationale

Key architectural decisions:

* Lifespan-based startup initialisation (non-deprecated FastAPI API)
* Idempotent ingestion logic
* Separation of startup and live update ingestion
* Persistent storage via Docker volumes
* Local-first LLM execution

This design mirrors production-grade RAG systems and avoids race conditions, unnecessary recomputation, and platform-specific issues.

---

## 8) Health Check

Verify that the API is running:

```
curl http://localhost:8000/health
```

Expected response:

```
{ "status": "ok" }
```

---

## 9) Summary

* The chatbot always starts with a valid vector database
* Knowledge can be updated dynamically at runtime
* Docker ensures reproducibility and persistence
* The system is extensible to new games and content sources
