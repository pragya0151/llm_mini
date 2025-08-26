# backend/embeddings.py
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from typing import List, Optional

# Create a reusable embeddings model (downloads on first run)
_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_vector_db(chunks: List[Document]) -> FAISS:
    """Build a FAISS vector store from chunks using MiniLM embeddings."""
    vector_db = FAISS.from_documents(chunks, _embeddings)
    return vector_db

def save_vector_db(vector_db: FAISS, path: str) -> None:
    vector_db.save_local(path)

def load_vector_db(path: str) -> Optional[FAISS]:
    try:
        return FAISS.load_local(path, _embeddings, allow_dangerous_deserialization=True)
    except Exception:
        return None
