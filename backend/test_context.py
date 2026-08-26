from app.rag.context_builder import build_context


query = "How does fake news affect social media users?"

context = build_context(query, top_k=3)

print("\n===== RAG CONTEXT =====\n")
print(context)