"""RAG orchestrator — wires all components together."""

from src.loader import load
from src.chunker import chunk
from src.embedder import embed_batch
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.generator import generate


class RAG:
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "default"):
        self._store = VectorStore(persist_dir=persist_dir, collection_name=collection_name)
        self._retriever = Retriever(store=self._store)

    def ingest(self, path: str, chunk_size: int = 500, overlap: int = 50) -> int:
        """Load, chunk, embed, and store documents. Returns number of chunks stored."""
        docs = load(path)
        all_chunks = []
        for doc in docs:
            all_chunks.extend(chunk(doc, chunk_size=chunk_size, overlap=overlap))

        if not all_chunks:
            return 0

        texts = [c.text for c in all_chunks]
        embeddings = embed_batch(texts)
        chunk_dicts = [{"text": c.text, "metadata": c.metadata} for c in all_chunks]
        self._store.add(chunk_dicts, embeddings)
        return len(all_chunks)

    def ask(self, query: str, top_k: int = 5) -> str:
        """Retrieve relevant chunks and generate answer."""
        results = self._retriever.retrieve(query, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin liên quan trong tài liệu."
        context = [r["text"] for r in results]
        return generate(query, context)

    def status(self) -> dict:
        """Return store statistics."""
        return {"chunks": self._store.count()}

    def reset(self) -> None:
        """Delete all data."""
        self._store.delete_collection()
