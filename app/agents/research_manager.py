from typing import List

from fastapi import HTTPException

from app.agents.literature_agent import LiteratureAgent
from app.agents.analysis_agent import AnalysisAgent
from app.agents.gap_agent import GapAgent
from app.agents.planning_agent import PlanningAgent

from app.rag.retriever import retrieve


class ResearchManager:
    """
    Main orchestrator for ResearchPilot AI.

    Pipeline:

        Research Topic
             ↓
        RAG Evidence
             ↓
        LiteratureAgent
             ↓
        AnalysisAgent
             ↓
        GapAgent
             ↓
        PlanningAgent
             ↓
        Final Research Plan
    """

    def __init__(self):

        self.literature_agent = LiteratureAgent()
        self.analysis_agent = AnalysisAgent()
        self.gap_agent = GapAgent()
        self.planning_agent = PlanningAgent()

    # ========================================================
    # RAG Evidence
    # ========================================================

    def retrieve_research_evidence(
        self,
        research_topic: str,
        top_k: int = 5,
        project_id: str | None = None,
    ) -> list[dict]:
        """
        Retrieve relevant research evidence from ChromaDB.

        This does not call Gemini.
        """

        try:
            results = retrieve(query=research_topic, top_k=top_k, project_id=project_id)
        except HTTPException as exc:
            if exc.status_code == 503:
                results = []
            else:
                raise

        evidence = []

        for i, result in enumerate(
            results,
            start=1
        ):
            evidence.append(
                {
                    "id": i,
                    "text": result.get(
                        "text",
                        ""
                    ),
                    "source": result.get(
                        "source",
                        "Unknown"
                    ),
                    "page": result.get(
                        "page",
                        "Unknown"
                    ),
                    "distance": result.get(
                        "distance"
                    )
                }
            )

        return evidence

    # ========================================================
    # Complete Research Workflow
    # ========================================================

    def run_research_workflow(
        self,
        research_topic: str,
        papers: List[dict],
        evidence_top_k: int = 5,
        project_id: str | None = None,
    ):
        """
        Run the complete multi-agent research workflow.

        RAG evidence is retrieved first and supplied to the
        AnalysisAgent for evidence-aware research-gap analysis.
        """

        # ====================================================
        # 1. Retrieve Research Evidence
        # ====================================================

        evidence = self.retrieve_research_evidence(
            research_topic=research_topic,
            top_k=evidence_top_k,
            project_id=project_id,
        )

        # ====================================================
        # 2. Literature Agent
        # ====================================================

        literature_result = self.literature_agent.run(
            papers=papers
        )

        paper_analyses = (
            literature_result["paper_analyses"]
        )

        theme_analysis = (
            literature_result["theme_analysis"]
        )

        paper_analysis_text = [
            analysis.model_dump_json()
            for analysis in paper_analyses
        ]

        # ====================================================
        # 3. Analysis Agent
        # ====================================================

        gap_analysis = self.analysis_agent.run(
            research_topic=research_topic,
            paper_analyses=paper_analysis_text,
            theme_analysis=theme_analysis.model_dump_json(),
            evidence=evidence
        )

        research_gaps = [
            gap.gap_title
            for gap in gap_analysis.gaps
        ]

        # ====================================================
        # 4. Gap Agent
        # ====================================================

        gap_result = self.gap_agent.run(
            research_topic=research_topic,
            research_gaps=research_gaps,
            evidence=evidence
        )

        dataset_recommendations = (
            gap_result["dataset_recommendations"]
        )

        tool_recommendations = (
            gap_result["tool_recommendations"]
        )

        dataset_names = [
            dataset.name
            for dataset
            in dataset_recommendations.recommendations
        ]

        tool_names = [
            tool.name
            for tool
            in tool_recommendations.recommendations
        ]

        # ====================================================
        # 5. Planning Agent
        # ====================================================

        planning_result = self.planning_agent.run(
            research_topic=research_topic,
            research_gaps=research_gaps,
            available_datasets=dataset_names,
            available_tools=tool_names,
            evidence=evidence
        )

        methodology_recommendations = (
            planning_result[
                "methodology_recommendations"
            ]
        )

        experiment_plan = (
            planning_result[
                "experiment_plan"
            ]
        )

        roadmap = (
            planning_result[
                "roadmap"
            ]
        )

        # ====================================================
        # 6. Final Result
        # ====================================================

        return {
            "research_topic": research_topic,

            "evidence": evidence,

            "paper_analyses": paper_analyses,

            "theme_analysis": theme_analysis,

            "gap_analysis": gap_analysis,

            "dataset_recommendations":
                dataset_recommendations,

            "tool_recommendations":
                tool_recommendations,

            "methodology_recommendations":
                methodology_recommendations,

            "experiment_plan":
                experiment_plan,

            "roadmap":
                roadmap
        }
