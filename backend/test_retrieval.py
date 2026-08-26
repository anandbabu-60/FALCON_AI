import chromadb

from app.rag.embeddings import generate_embeddings


client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    name="research_papers"
)

print("Number of stored chunks:", collection.count())

query = "machine learning research"

query_embedding = generate_embeddings([query])[0]

result = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("\nRetrieved documents:")

for i, document in enumerate(result["documents"][0]):
    print(f"\n--- Result {i + 1} ---")
    print(document[:500])

print("\nMetadata:")

for metadata in result["metadatas"][0]:
    print(metadata)