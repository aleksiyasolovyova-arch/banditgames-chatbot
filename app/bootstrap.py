import logging
from langchain_community.vectorstores import Chroma
from app.config import CHROMA_PATH, COLLECTION_NAME, DATA_PATH
from app.embeddings import get_embedding_function
from app.ingest import load_documents, split_documents, add_chunk_ids

logger = logging.getLogger("bootstrap")
logging.basicConfig(level=logging.INFO)


def bootstrap_vector_db():
    logger.info("BOOTSTRAP: Starting vector DB bootstrap")

    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=get_embedding_function(),
    )

    try:
        count = db._collection.count()
    except Exception:
        count = 0

    logger.info(f"BOOTSTRAP: Existing embeddings count = {count}")

    if count > 0:
        logger.info("BOOTSTRAP: Vector DB already initialised, skipping ingestion")
        return

    logger.info("BOOTSTRAP: Vector DB empty, running initial ingestion")

    docs = load_documents(DATA_PATH)
    chunks = add_chunk_ids(split_documents(docs))

    if chunks:
        db.add_documents(
            documents=chunks,
            ids=[c.metadata["chunk_id"] for c in chunks],
        )
        db.persist()

    logger.info(f"BOOTSTRAP: Initial ingestion complete ({len(chunks)} chunks)")
