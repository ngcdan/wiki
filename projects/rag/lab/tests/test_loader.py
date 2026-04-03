import tempfile
import os
from src.loader import load, Document


def test_load_txt_file():
    """load() on a .txt file should return a Document with content and metadata."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello world")
        f.flush()
        try:
            docs = load(f.name)
            assert len(docs) == 1
            assert docs[0].content == "Hello world"
            assert docs[0].metadata["type"] == "txt"
            assert docs[0].metadata["source"] == f.name
        finally:
            os.unlink(f.name)


def test_load_md_file():
    """load() on a .md file should return a Document."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Title\n\nSome content")
        f.flush()
        try:
            docs = load(f.name)
            assert len(docs) == 1
            assert docs[0].metadata["type"] == "md"
        finally:
            os.unlink(f.name)


def test_load_directory():
    """load() on a directory should return Documents for all supported files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        for name in ["a.txt", "b.md", "c.log"]:
            with open(os.path.join(tmpdir, name), "w") as f:
                f.write(f"content of {name}")

        docs = load(tmpdir)
        # Should load .txt and .md, skip .log
        assert len(docs) == 2
