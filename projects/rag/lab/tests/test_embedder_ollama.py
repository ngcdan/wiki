import os
from importlib import reload
from unittest.mock import patch, MagicMock


def test_embed_uses_ollama_when_configured():
    """When EMBED_PROVIDER=ollama, embed() should call Ollama, not OpenAI."""
    mock_ollama = MagicMock()
    mock_ollama.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}

    with patch.dict(os.environ, {"EMBED_PROVIDER": "ollama"}):
        import src.embedder
        reload(src.embedder)
        with patch("src.embedder._get_ollama_client", return_value=mock_ollama):
            result = src.embedder.embed("hello")

    assert result == [0.1, 0.2, 0.3]
    mock_ollama.embed.assert_called_once()
