import os
import glob
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def load_documents(data_path: str) -> List[Document]:
    docs: List[Document] = []

    # PDFs
    for pdf_path in glob.glob(os.path.join(data_path, "**/*.pdf"), recursive=True):
        loader = PyPDFLoader(pdf_path)
        docs.extend(loader.load())

    # Markdown / txt
    for path in glob.glob(os.path.join(data_path, "**/*.md"), recursive=True):
        loader = TextLoader(path, encoding="utf-8")
        docs.extend(loader.load())

    for path in glob.glob(os.path.join(data_path, "**/*.txt"), recursive=True):
        loader = TextLoader(path, encoding="utf-8")
        docs.extend(loader.load())

    return docs

def split_documents(documents: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=120,
        length_function=len,
    )
    return splitter.split_documents(documents)

def add_chunk_ids(chunks: List[Document]) -> List[Document]:
    """
    Create stable IDs like: rules/connect_four.md:chunk:00012
    """
    counters = {}
    for d in chunks:
        source = d.metadata.get("source", "unknown")
        # Make it nicer/portable
        source_norm = source.replace("\\", "/")
        counters.setdefault(source_norm, 0)
        idx = counters[source_norm]
        counters[source_norm] += 1
        d.metadata["chunk_id"] = f"{source_norm}:chunk:{idx:05d}"
    return chunks
