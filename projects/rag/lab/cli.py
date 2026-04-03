"""RAG Lab CLI."""

import click
from src.rag import RAG


@click.group()
def main():
    """RAG Lab — load documents and ask questions."""
    pass


@main.command()
@click.argument("path")
@click.option("--chunk-size", default=500, help="Chunk size in characters")
@click.option("--overlap", default=50, help="Overlap between chunks")
def ingest(path, chunk_size, overlap):
    """Ingest documents from PATH into the vector store."""
    rag = RAG()
    count = rag.ingest(path, chunk_size=chunk_size, overlap=overlap)
    click.echo(f"Ingested {count} chunks.")


@main.command()
@click.argument("question")
@click.option("--top-k", default=5, help="Number of chunks to retrieve")
def ask(question, top_k):
    """Ask a question about ingested documents."""
    rag = RAG()
    answer = rag.ask(question, top_k=top_k)
    click.echo(answer)


@main.command()
def status():
    """Show store statistics."""
    rag = RAG()
    info = rag.status()
    click.echo(f"Chunks in store: {info['chunks']}")


@main.command()
def reset():
    """Delete all data from the vector store."""
    if click.confirm("Delete all data?"):
        rag = RAG()
        rag.reset()
        click.echo("Store reset.")


if __name__ == "__main__":
    main()
