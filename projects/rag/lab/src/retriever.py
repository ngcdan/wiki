"""Retrieval pipeline — connects embedder + vector store."""

from src.embedder import embed
from src.vector_store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore):
        self._store = store

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Embed query and search vector store for relevant chunks."""
        query_embedding = embed(query)
        return self._store.search(query_embedding=query_embedding, top_k=top_k)
