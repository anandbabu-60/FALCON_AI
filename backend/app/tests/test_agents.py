from app.agents.research_manager import ResearchManager


def test_research_manager_initializes():

    manager = ResearchManager()

    assert manager is not None

    assert manager.literature_agent is not None
    assert manager.analysis_agent is not None
    assert manager.gap_agent is not None
    assert manager.planning_agent is not None


def test_research_manager_retrieves_evidence():

    manager = ResearchManager()

    evidence = manager.retrieve_research_evidence(
        research_topic="population",
        top_k=3
    )

    assert isinstance(evidence, list)

    assert len(evidence) <= 3


def test_research_evidence_structure():

    manager = ResearchManager()

    evidence = manager.retrieve_research_evidence(
        research_topic="population",
        top_k=3
    )

    if not evidence:
        return

    item = evidence[0]

    assert "id" in item
    assert "text" in item
    assert "source" in item
    assert "page" in item
    assert "distance" in item