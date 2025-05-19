# vector_store.py   # RAG Vector Store Setup

import os
from typing import Dict, List, Tuple
from openai import OpenAI
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document

# Initialize embedding model
embeddings_model = OpenAIEmbeddings()

# Path to persist the FAISS index
INDEX_DIR = os.getenv("FAISS_INDEX_DIR", "faiss_index")

def build_vector_store(corpus: Dict[str, str]) -> FAISS:
    """
    Build (or load) a FAISS vector store from a dict of {doc_id: text}.
    - Splits long documents into chunks.
    - Embeds chunks and indexes them.
    Returns the FAISS store instance.
    """
    # Check for existing index
    if os.path.exists(INDEX_DIR):
        return FAISS.load_local(INDEX_DIR, embeddings_model)

    # Prepare documents
    docs: List[Document] = []
    for doc_id, text in corpus.items():
        # Simple text splitter; you can swap in RecursiveCharacterTextSplitter if desired
        chunks = [
            text[i : i + 1000]
            for i in range(0, len(text), 1000)
        ]
        for idx, chunk in enumerate(chunks):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={"source": doc_id, "chunk": idx},
                )
            )

    # Build new index
    store = FAISS.from_documents(docs, embeddings_model)
    # Persist it
    store.save_local(INDEX_DIR)
    return store

def retrieve_relevant(doc_store: FAISS, query: str, k: int = 5) -> List[Tuple[str, str]]:
    """
    Perform a similarity search against the vector store.
    Returns up to k tuples of (source_doc_id, chunk_text).
    """
    results = doc_store.similarity_search(query, k=k)
    # Extract source & text
    return [
        (res.metadata.get("source", ""), res.page_content) 
        for res in results
    ]
