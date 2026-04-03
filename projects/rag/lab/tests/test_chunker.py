from src.loader import Document
from src.chunker import chunk, Chunk


def test_fixed_size_chunking():
    """Fixed-size chunking should split by character count."""
    doc = Document(content="a" * 100, metadata={"source": "test.txt", "type": "txt"})
    chunks = chunk(doc, strategy="fixed", chunk_size=30, overlap=0)

    assert len(chunks) == 4  # 100 / 30 = 3.33 → 4
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].metadata["chunk_index"] == 0


def test_recursive_chunking_splits_on_newlines():
    """Recursive chunking should prefer splitting on paragraph boundaries."""
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    doc = Document(content=text, metadata={"source": "test.md", "type": "md"})
    chunks = chunk(doc, strategy="recursive", chunk_size=30, overlap=0)

    assert len(chunks) >= 2
    # Should not split mid-paragraph
    assert "Paragraph one." in chunks[0].text


def test_overlap():
    """Chunks with overlap should share characters at boundaries."""
    doc = Document(content="abcdefghij" * 5, metadata={"source": "t.txt", "type": "txt"})
    chunks = chunk(doc, strategy="fixed", chunk_size=20, overlap=5)

    if len(chunks) >= 2:
        # End of chunk 0 should overlap with start of chunk 1
        assert chunks[0].text[-5:] == chunks[1].text[:5]
