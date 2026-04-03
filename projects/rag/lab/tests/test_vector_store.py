import tempfile
import os
from src.vector_store import VectorStore


def test_add_and_search():
    """Add chunks then search should return relevant results."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = VectorStore(persist_dir=tmpdir, collection_name="test")

        chunks = [
            {"text": "hello world", "metadata": {"source": "a.txt", "chunk_index": 0}},
            {"text": "goodbye world", "metadata": {"source": "b.txt", "chunk_index": 0}},
        ]
        embeddings = [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ]

        store.add(chunks, embeddings)
        results = store.search(query_embedding=[1.0, 0.0, 0.0], top_k=1)

        assert len(results) == 1
        assert results[0]["text"] == "hello world"


def test_delete_collection():
    """delete_collection should remove all data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = VectorStore(persist_dir=tmpdir, collection_name="test")

        chunks = [{"text": "hello", "metadata": {"source": "a.txt", "chunk_index": 0}}]
        embeddings = [[1.0, 0.0]]

        store.add(chunks, embeddings)
        store.delete_collection()

        # Re-create store — should be empty
        store2 = VectorStore(persist_dir=tmpdir, collection_name="test")
        results = store2.search(query_embedding=[1.0, 0.0], top_k=1)
        assert len(results) == 0
