from unittest.mock import patch, MagicMock
from src.retriever import Retriever


def test_retrieve_returns_ranked_chunks():
    """retrieve() should embed query, search store, return results."""
    mock_store = MagicMock()
    mock_store.search.return_value = [
        {"text": "relevant chunk", "metadata": {"source": "a.txt"}, "score": 0.1},
    ]

    with patch("src.retriever.embed", return_value=[1.0, 0.0, 0.0]):
        retriever = Retriever(store=mock_store)
        results = retriever.retrieve("what is RAG?", top_k=1)

    assert len(results) == 1
    assert results[0]["text"] == "relevant chunk"
