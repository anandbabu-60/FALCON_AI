from app.rag.ingest import ingest_pdf


chunks = ingest_pdf("sample.pdf")

print("\nFirst chunk:")
print(chunks[0]["text"])

print("\nMetadata:")
print(chunks[0]["metadata"])