from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import EMBED_MODEL

_embedding_singleton = None

def get_embedding_function():
    global _embedding_singleton
    if _embedding_singleton is None:
        _embedding_singleton = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            # Good defaults; adjust if you want cosine normalized vectors
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_singleton
