"""Embedding wrapper — provider-agnostic interface."""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_DEFAULT_MODEL = "text-embedding-3-small"


def _get_openai_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed(text: str, model: str = _DEFAULT_MODEL) -> list[float]:
    """Embed a single text string into a vector."""
    client = _get_openai_client()
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


def embed_batch(texts: list[str], model: str = _DEFAULT_MODEL) -> list[list[float]]:
    """Embed multiple texts into vectors."""
    client = _get_openai_client()
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in response.data]
