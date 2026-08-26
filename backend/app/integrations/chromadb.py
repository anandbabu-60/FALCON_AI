import uuid

import chromadb


# ============================================================
# ChromaDB
# ============================================================

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="research_papers",
    embedding_function=None
)


# ============================================================
# Add Chunks
# ============================================================

def add_chunks(
    chunks: list[dict],
    embeddings: list[list[float]]
):
    """
    Store document chunks and their embeddings in ChromaDB.

    Each chunk receives a globally unique ID so that multiple
    PDFs can safely be ingested without ID collisions.
    """

    if not chunks:
        return {
            "stored": 0
        }

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks must match number of embeddings."
        )

    ids = [
        f"chunk-{uuid.uuid4().hex}"
        for _ in chunks
    ]

    collection.add(
        ids=ids,

        documents=[
            chunk["text"]
            for chunk in chunks
        ],

        embeddings=embeddings,

        metadatas=[
            chunk["metadata"]
            for chunk in chunks
        ],
    )

    return {
        "stored": len(chunks)
    }