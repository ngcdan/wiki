"""Module 2 demo: ChromaDB CRUD operations with synthetic vectors."""

import sys
import tempfile
sys.path.insert(0, ".")

from src.vector_store import VectorStore


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = VectorStore(persist_dir=tmpdir, collection_name="demo")

        # Add synthetic data
        chunks = [
            {"text": "Python is a programming language", "metadata": {"source": "lang.txt", "chunk_index": 0}},
            {"text": "Java is also a programming language", "metadata": {"source": "lang.txt", "chunk_index": 1}},
            {"text": "Cats are cute animals", "metadata": {"source": "animals.txt", "chunk_index": 0}},
        ]
        embeddings = [
            [1.0, 0.1, 0.0],
            [0.9, 0.2, 0.0],
            [0.0, 0.1, 1.0],
        ]

        print("Adding 3 chunks...")
        store.add(chunks, embeddings)
        print(f"Count: {store.count()}")

        print("\nSearching for programming-like query [1.0, 0.0, 0.0]:")
        results = store.search(query_embedding=[1.0, 0.0, 0.0], top_k=2)
        for r in results:
            print(f"  score={r['score']:.4f} | {r['text']}")

        print("\nSearching for animal-like query [0.0, 0.0, 1.0]:")
        results = store.search(query_embedding=[0.0, 0.0, 1.0], top_k=1)
        for r in results:
            print(f"  score={r['score']:.4f} | {r['text']}")

        print("\nDeleting collection...")
        store.delete_collection()
        print("Done.")


if __name__ == "__main__":
    main()
