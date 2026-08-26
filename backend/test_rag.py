from app.rag.rag_pipeline import answer_question


query = "How does fake news affect social media users?"

result = answer_question(
    query=query,
    top_k=3
)

print("\n===== RAG ANSWER =====\n")
print(result["answer"])

print("\n===== CITATIONS =====\n")

for citation in result["citations"]:
    print(
        f"[Evidence {citation['id']}] "
        f"{citation['source']} - "
        f"Page {citation['page']}"
    )