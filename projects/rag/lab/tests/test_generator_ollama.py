import os
from importlib import reload
from unittest.mock import patch, MagicMock


def test_generate_uses_ollama_when_configured():
    """When LLM_PROVIDER=ollama, generate() should call Ollama."""
    mock_ollama = MagicMock()
    mock_ollama.chat.return_value = {"message": {"content": "Ollama says 42."}}

    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}):
        import src.generator
        reload(src.generator)
        with patch("src.generator._get_ollama_client", return_value=mock_ollama):
            result = src.generator.generate("What?", context=["42"])

    assert "42" in result
    mock_ollama.chat.assert_called_once()
