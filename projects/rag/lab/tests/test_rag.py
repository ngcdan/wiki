from unittest.mock import patch, MagicMock
from src.rag import RAG


def test_ask_wires_retriever_and_generator():
    """ask() should retrieve chunks then generate answer."""
    with patch("src.rag.VectorStore"), \
         patch("src.rag.Retriever") as MockRetriever, \
         patch("src.rag.generate", return_value="answer") as mock_gen:

        mock_retriever_instance = MockRetriever.return_value
        mock_retriever_instance.retrieve.return_value = [
            {"text": "chunk1", "metadata": {}, "score": 0.1},
        ]

        rag = RAG(persist_dir="/tmp/test_rag")
        result = rag.ask("question?")

    assert result == "answer"
    mock_retriever_instance.retrieve.assert_called_once()
    mock_gen.assert_called_once()
