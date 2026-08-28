from app.rag.retriever import retrieve


def build_context(query: str, top_k: int = 5) -> tuple[str, list[dict]]:
    results = retrieve(query, top_k)

    if not results:
        return "No relevant information was found.", []

    context_parts = []
    citations = []

    for i, result in enumerate(results, start=1):
        source = result.get("source", "Unknown")
        page = result.get("page", "Unknown")
        text = result.get("text", "")

        context_parts.append(
            f"""[Evidence {i}]
Source: {source}
Page: {page}

{text}
"""
        )

        citations.append(
            {
                "id": i,
                "source": source,
                "page": page,
            }
        )

    return "\n\n".join(context_parts), citations