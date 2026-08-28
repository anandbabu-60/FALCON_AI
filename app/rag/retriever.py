from fastapi import HTTPException


# ============================================================
# Retrieval
# ============================================================

def retrieve(
    query: str,
    top_k: int = 5,
    distance_threshold: float = 1.20,
    source: str | None = None,
    project_id: str | None = None,
) -> list[dict]:
    """
    Retrieve research evidence relevant to a query.

    Smaller ChromaDB distances generally indicate greater
    similarity.

    If source is provided, retrieval is restricted to that
    document.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not query or not query.strip():
        return []

    if top_k <= 0:
        return []

    # --------------------------------------------------------
    # Generate query embedding
    # --------------------------------------------------------

    try:
        from app.rag.embeddings import generate_embeddings
        query_embedding = generate_embeddings([query])[0]
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="RAG dependencies are not installed. Install requirements-ai.txt to enable semantic search.") from exc

    # --------------------------------------------------------
    # Optional document filter
    # --------------------------------------------------------

    where = None

    filters = []
    if source:
        filters.append({"source": source})
    if project_id:
        filters.append({"project_id": project_id})
    if len(filters) == 1:
        where = filters[0]
    elif filters:
        where = {"$and": filters}

    # --------------------------------------------------------
    # Search ChromaDB
    # --------------------------------------------------------

    try:
        from app.integrations.chromadb import collection
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k, where=where, include=["documents", "metadatas", "distances"])
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="ChromaDB is not installed. Install requirements-ai.txt to enable semantic search.") from exc
    except Exception:
        return []

    # --------------------------------------------------------
    # Handle empty results
    # --------------------------------------------------------

    if not results.get("documents"):
        return []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved_chunks = []

    # --------------------------------------------------------
    # Build evidence
    # --------------------------------------------------------

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        # Reject weak evidence
        if distance > distance_threshold:
            continue

        metadata = metadata or {}

        retrieved_chunks.append(
            {
                "text": document,
                "source": metadata.get(
                    "source",
                    "Unknown"
                ),
                "page": metadata.get(
                    "page",
                    "Unknown"
                ),
                "distance": distance,
            }
        )

    return retrieved_chunks
