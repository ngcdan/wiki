"""LLM generation — provider-agnostic interface."""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

_DEFAULT_MODEL = "claude-sonnet-4-20250514"


def _get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate(query: str, context: list[str], model: str = _DEFAULT_MODEL) -> str:
    """Generate answer from query + retrieved context chunks."""
    context_text = "\n\n---\n\n".join(context)
    prompt = f"""Dựa trên ngữ cảnh sau, hãy trả lời câu hỏi. Nếu ngữ cảnh không chứa đủ thông tin, hãy nói rõ.

Ngữ cảnh:
{context_text}

Câu hỏi: {query}"""

    client = _get_anthropic_client()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
