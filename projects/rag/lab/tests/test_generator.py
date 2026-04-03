from unittest.mock import patch, MagicMock
from src.generator import generate


def test_generate_returns_string():
    """generate() should return LLM response as string."""
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="The answer is 42.")]
    )

    with patch("src.generator._get_anthropic_client", return_value=mock_client):
        result = generate("What is the answer?", context=["The answer to everything is 42."])

    assert isinstance(result, str)
    assert "42" in result
