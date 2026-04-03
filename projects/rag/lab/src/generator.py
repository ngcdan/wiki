"""LLM generation — provider-agnostic interface."""

import os
from dotenv import load_dotenv
from anthropic import Anthropic
import ollama as ollama_lib

load_dotenv()

_ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-4-20250514"


def _get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _get_ollama_client():
    return ollama_lib.Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))


def generate(query: str, context: list[str], model: str | None = None) -> str:
    """Generate answer from query + retrieved context chunks."""
    context_text = "\n\n---\n\n".join(context)
    prompt = f"""Dựa trên ngữ cảnh sau, hãy trả lời câu hỏi. Nếu ngữ cảnh không chứa đủ thông tin, hãy nói rõ.

Ngữ cảnh:
{context_text}

Câu hỏi: {query}"""

    provider = os.getenv("LLM_PROVIDER", "anthropic")
    if provider == "ollama":
        client = _get_ollama_client()
        m = model or os.getenv("OLLAMA_LLM_MODEL", "llama3")
        response = client.chat(model=m, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    else:
        client = _get_anthropic_client()
        m = model or _ANTHROPIC_DEFAULT_MODEL
        response = client.messages.create(
            model=m,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
