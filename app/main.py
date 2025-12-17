import os
import shutil
from fastapi import FastAPI
from pydantic import BaseModel

from langchain_community.vectorstores import Chroma

from app.config import DATA_PATH, CHROMA_PATH, COLLECTION_NAME
from app.embeddings import get_embedding_function
from app.ingest import load_documents, split_documents, add_chunk_ids
from app.rag import retrieve_context, generate_answer
from app.cache import cache_get, cache_set

app = FastAPI(title="Game Platform RAG Chatbot")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    cached: bool

class IngestResponse(BaseModel):
    ingested_chunks: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    payload = {"query": req.query}

    cached = cache_get("chat", payload)
    if cached:
        return ChatResponse(answer=cached, cached=True)

    context_text, sources = retrieve_context(req.query)
    answer = generate_answer(req.query, context_text, sources)

    cache_set("chat", payload, answer)
    return ChatResponse(answer=answer, cached=False)

@app.post("/ingest", response_model=IngestResponse)
def ingest(reset: bool = False):
    if reset:
        db = Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=CHROMA_PATH,
            embedding_function=get_embedding_function(),
        )
        db.delete_collection()

    docs = load_documents(DATA_PATH)
    chunks = add_chunk_ids(split_documents(docs))

    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function(),
    )

    if chunks:
        db.add_documents(
            documents=chunks,
            ids=[c.metadata["chunk_id"] for c in chunks],
        )
        db.persist()

    return IngestResponse(ingested_chunks=len(chunks))