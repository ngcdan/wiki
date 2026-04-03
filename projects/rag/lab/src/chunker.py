"""Text chunking strategies."""

from dataclasses import dataclass
from src.loader import Document

SEPARATORS = ["\n\n", "\n", ". ", " "]


@dataclass
class Chunk:
    text: str
    metadata: dict


def chunk(
    doc: Document,
    strategy: str = "recursive",
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """Split a Document into Chunks."""
    if strategy == "fixed":
        texts = _fixed_split(doc.content, chunk_size, overlap)
    elif strategy == "recursive":
        texts = _recursive_split(doc.content, chunk_size, overlap, SEPARATORS)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return [
        Chunk(
            text=t,
            metadata={**doc.metadata, "chunk_index": i},
        )
        for i, t in enumerate(texts)
    ]


def _fixed_split(text: str, size: int, overlap: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap if overlap else end
    return chunks


def _recursive_split(text: str, size: int, overlap: int, separators: list[str]) -> list[str]:
    if len(text) <= size:
        return [text] if text.strip() else []

    # Try each separator
    for sep in separators:
        if sep in text:
            parts = text.split(sep)
            chunks = []
            current = ""
            for part in parts:
                candidate = current + sep + part if current else part
                if len(candidate) <= size:
                    current = candidate
                else:
                    if current:
                        chunks.append(current)
                    current = part
            if current:
                chunks.append(current)

            # If we actually split, return
            if len(chunks) > 1:
                return chunks

    # Fallback to fixed split
    return _fixed_split(text, size, overlap)
