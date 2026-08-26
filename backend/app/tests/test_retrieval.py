from app.rag.retriever import retrieve


def test_retrieval_returns_results():
    results = retrieve(
        query="population",
        top_k=3
    )

    assert isinstance(results, list)


def test_retrieval_result_structure():
    results = retrieve(
        query="population",
        top_k=3
    )

    if not results:
        return

    result = results[0]

    assert "text" in result
    assert "source" in result
    assert "page" in result
    assert "distance" in result


def test_retrieval_respects_top_k():
    results = retrieve(
        query="population",
        top_k=3
    )

    assert len(results) <= 3