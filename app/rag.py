from typing import Tuple, List
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from app.config import CHROMA_PATH, COLLECTION_NAME, TOP_K, OLLAMA_BASE_URL, OLLAMA_MODEL
from app.embeddings import get_embedding_function

PROMPT_TEMPLATE = """
You are a helpful support chatbot for a game platform that hosts multiple board games.

Rules:
- Use ONLY the provided context.
- If the answer is not in the context, say: "I don’t have that information in my knowledge base yet."
- When explaining rules, present them in clear, numbered steps.
- If the user question seems like a platform navigation question, answer as platform support.
- Keep it concise but complete.

CONTEXT:
{context}

USER QUESTION:
{question}

OUTPUT FORMAT:
1) Direct answer
2) Step-by-step (if rules/how-to)
3) Sources (list the source chunk ids)
"""

def get_db() -> Chroma:
    embedding_function = get_embedding_function()
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_function,
    )

def retrieve_context(query: str) -> Tuple[str, List[str]]:
    db = get_db()
    results = db.similarity_search_with_score(query, k=TOP_K)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    sources = [doc.metadata.get("chunk_id") for doc, _score in results]
    return context_text, sources

def generate_answer(query: str, context_text: str, sources: List[str]) -> str:
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).format(
        context=context_text,
        question=query,
    )

    llm = Ollama(base_url=OLLAMA_BASE_URL, model=OLLAMA_MODEL)
    response = llm.invoke(prompt)

    # Ensure we always include sources at the end (even if model forgets)
    sources_block = "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources if s)
    return f"{response}{sources_block}"
