from unittest.mock import patch, MagicMock
from src.embedder import embed, embed_batch


def test_embed_returns_list_of_floats():
    """embed() should return a list of floats (vector)."""
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]

    with patch("src.embedder._get_openai_client") as mock_client:
        mock_client.return_value.embeddings.create.return_value = mock_response
        result = embed("hello world")

    assert isinstance(result, list)
    assert all(isinstance(x, float) for x in result)
    assert len(result) == 3


def test_embed_batch_returns_list_of_vectors():
    """embed_batch() should return a list of vectors."""
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=[0.1, 0.2]),
        MagicMock(embedding=[0.3, 0.4]),
    ]

    with patch("src.embedder._get_openai_client") as mock_client:
        mock_client.return_value.embeddings.create.return_value = mock_response
        result = embed_batch(["hello", "world"])

    assert len(result) == 2
    assert all(isinstance(v, list) for v in result)
