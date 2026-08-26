from typing import List, Optional

from app.services.methodology_planner import recommend_methodology
from app.services.experiment_planner import plan_experiments
from app.services.roadmap_generator import generate_roadmap


class PlanningAgent:
    """
    Coordinates the research planning stage.

    Responsibilities:
    1. Recommend a suitable research methodology.
    2. Create an experiment plan.
    3. Generate a research roadmap.
    """

    def recommend_methodology(
        self,
        research_topic: str,
        research_gaps: List[str],
        available_datasets: List[str],
        available_tools: List[str],
        evidence: Optional[List[dict]] = None
    ):
        return recommend_methodology(
            research_topic=research_topic,
            research_gaps=research_gaps,
            available_datasets=available_datasets,
            available_tools=available_tools,
            evidence=evidence
        )

    def plan_experiments(
        self,
        research_topic: str,
        research_gaps: List[str],
        methodology: str,
        datasets: List[str],
        tools: List[str],
        evidence: Optional[List[dict]] = None
    ):
        return plan_experiments(
            research_topic=research_topic,
            research_gaps=research_gaps,
            methodology=methodology,
            datasets=datasets,
            tools=tools,
            evidence=evidence
        )

    def generate_roadmap(
        self,
        research_topic: str,
        research_gaps: List[str],
        methodology: str,
        experiment_plan: str,
        evidence: Optional[List[dict]] = None
    ):
        return generate_roadmap(
            research_topic=research_topic,
            research_gaps=research_gaps,
            methodology=methodology,
            experiment_plan=experiment_plan,
            evidence=evidence
        )

    def run(
        self,
        research_topic: str,
        research_gaps: List[str],
        available_datasets: List[str],
        available_tools: List[str],
        evidence: Optional[List[dict]] = None
    ):
        methodology_recommendations = (
            self.recommend_methodology(
                research_topic=research_topic,
                research_gaps=research_gaps,
                available_datasets=available_datasets,
                available_tools=available_tools,
                evidence=evidence
            )
        )

        methodology_text = (
            methodology_recommendations.model_dump_json()
        )

        experiment_plan = self.plan_experiments(
            research_topic=research_topic,
            research_gaps=research_gaps,
            methodology=methodology_text,
            datasets=available_datasets,
            tools=available_tools,
            evidence=evidence
        )

        experiment_text = (
            experiment_plan.model_dump_json()
        )

        roadmap = self.generate_roadmap(
            research_topic=research_topic,
            research_gaps=research_gaps,
            methodology=methodology_text,
            experiment_plan=experiment_text,
            evidence=evidence
        )

        return {
            "methodology_recommendations":
                methodology_recommendations,

            "experiment_plan":
                experiment_plan,

            "roadmap":
                roadmap
        }