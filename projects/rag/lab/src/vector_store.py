"""ChromaDB wrapper — persistent vector store."""

import chromadb


class VectorStore:
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "default"):
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def add(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        """Add chunks with their embeddings to the store."""
        ids = [f"{c['metadata'].get('source', 'unknown')}_{c['metadata'].get('chunk_index', i)}" for i, c in enumerate(chunks)]
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
        )

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """Search for most similar chunks."""
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        if not results["documents"][0]:
            return []
        return [
            {
                "text": doc,
                "metadata": meta,
                "score": dist,
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    def delete_collection(self) -> None:
        """Delete the entire collection."""
        self._client.delete_collection(self._collection.name)

    def count(self) -> int:
        """Return number of items in collection."""
        return self._collection.count()
