import chromadb

from app.rag.embeddings import generate_embeddings


# ============================================================
# ChromaDB
# ============================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="research_papers"
)


# ============================================================
# Retrieval
# ============================================================

def retrieve(
    query: str,
    top_k: int = 5,
    distance_threshold: float = 1.20,
    source: str | None = None
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

    query_embedding = generate_embeddings(
        [query]
    )[0]

    # --------------------------------------------------------
    # Optional document filter
    # --------------------------------------------------------

    where = None

    if source:
        where = {
            "source": source
        }

    # --------------------------------------------------------
    # Search ChromaDB
    # --------------------------------------------------------

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

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