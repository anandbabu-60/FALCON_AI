from app.rag.rag_pipeline import answer_question


def test_rag_returns_expected_structure():
    result = answer_question(
        query="population",
        top_k=3
    )

    assert isinstance(result, dict)

    assert "answer" in result
    assert "citations" in result
    assert "citation_validation" in result


def test_citation_validation_structure():
    result = answer_question(
        query="population",
        top_k=3
    )

    validation = result["citation_validation"]

    assert "valid" in validation
    assert "cited_evidence" in validation
    assert "invalid_evidence" in validation


def test_citations_have_source_and_page():
    result = answer_question(
        query="population",
        top_k=3
    )

    for citation in result["citations"]:
        assert "id" in citation
        assert "source" in citation
        assert "page" in citation