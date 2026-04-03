"""Embedding wrapper — provider-agnostic interface."""

import os
from dotenv import load_dotenv
from openai import OpenAI
import ollama as ollama_lib

load_dotenv()

_OPENAI_DEFAULT_MODEL = "text-embedding-3-small"


def _get_openai_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _get_ollama_client():
    return ollama_lib.Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))


def embed(text: str, model: str | None = None) -> list[float]:
    """Embed a single text string into a vector."""
    provider = os.getenv("EMBED_PROVIDER", "openai")
    if provider == "ollama":
        client = _get_ollama_client()
        m = model or os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        response = client.embed(model=m, input=[text])
        return response["embeddings"][0]
    else:
        client = _get_openai_client()
        m = model or _OPENAI_DEFAULT_MODEL
        response = client.embeddings.create(input=[text], model=m)
        return response.data[0].embedding


def embed_batch(texts: list[str], model: str | None = None) -> list[list[float]]:
    """Embed multiple texts into vectors."""
    provider = os.getenv("EMBED_PROVIDER", "openai")
    if provider == "ollama":
        client = _get_ollama_client()
        m = model or os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        response = client.embed(model=m, input=texts)
        return response["embeddings"]
    else:
        client = _get_openai_client()
        m = model or _OPENAI_DEFAULT_MODEL
        response = client.embeddings.create(input=texts, model=m)
        return [item.embedding for item in response.data]
