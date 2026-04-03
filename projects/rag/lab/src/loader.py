"""Document loader — reads MD, PDF, TXT files."""

import os
from dataclasses import dataclass
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf"}


@dataclass
class Document:
    content: str
    metadata: dict


def load(path: str) -> list[Document]:
    """Load documents from a file or directory."""
    if os.path.isdir(path):
        docs = []
        for fname in sorted(os.listdir(path)):
            fpath = os.path.join(path, fname)
            if os.path.isfile(fpath):
                ext = os.path.splitext(fname)[1].lower()
                if ext in SUPPORTED_EXTENSIONS:
                    docs.extend(load(fpath))
        return docs

    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return load_pdf(path)

    # txt, md — read as plain text
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return [Document(content=content, metadata={"source": path, "type": ext.lstrip(".")})]


def load_pdf(path: str) -> list[Document]:
    """Load PDF — one Document per page."""
    reader = PdfReader(path)
    docs = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            docs.append(Document(
                content=text,
                metadata={"source": path, "type": "pdf", "page": i + 1},
            ))
    return docs
