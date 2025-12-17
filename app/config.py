import os
from dotenv import load_dotenv

load_dotenv()

def env(key: str, default: str | None = None) -> str:
    val = os.getenv(key, default)
    if val is None:
        raise RuntimeError(f"Missing required env var: {key}")
    return val

EMBED_MODEL = env("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

CHROMA_PATH = env("CHROMA_PATH", "/app/chroma")
COLLECTION_NAME = env("COLLECTION_NAME", "game_platform_kb")

DATA_PATH = env("DATA_PATH", "/app/data")

OLLAMA_BASE_URL = env("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = env("OLLAMA_MODEL", "mistral")

REDIS_URL = env("REDIS_URL", "redis://redis:6379/0")
CACHE_TTL_SECONDS = int(env("CACHE_TTL_SECONDS", "3600"))

TOP_K = int(env("TOP_K", "5"))
