from pathlib import Path

from app.rag.document_loader import load_pdf
from app.rag.chunker import chunk_pages
from app.rag.embeddings import generate_embeddings
from app.integrations.chromadb import add_chunks


def ingest_pdf(
    file_path: str,
    source_name: str | None = None,
    project_id: str | None = None,
):
    """
    Ingest a PDF into the RAG knowledge base.

    source_name is the user-facing filename that should appear
    in citations. If it is not provided, the PDF filename is used.
    """

    # ========================================================
    # 1. PDF → pages
    # ========================================================

    pages = load_pdf(file_path)

    # ========================================================
    # 2. Pages → chunks
    # ========================================================

    chunks = chunk_pages(pages)

    # ========================================================
    # 3. Store clean source metadata
    # ========================================================

    if source_name is None:
        source_name = Path(file_path).name

    for chunk in chunks:
        chunk["metadata"]["source"] = source_name
        if project_id:
            chunk["metadata"]["project_id"] = project_id

    # ========================================================
    # 4. Chunks → embeddings
    # ========================================================

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = generate_embeddings(
        texts
    )

    # ========================================================
    # 5. Store chunks + embeddings in ChromaDB
    # ========================================================

    result = add_chunks(
        chunks,
        embeddings
    )

    print("Pages:", len(pages))
    print("Chunks:", len(chunks))
    print("Stored:", result["stored"])
    print("Source:", source_name)

    return chunks
