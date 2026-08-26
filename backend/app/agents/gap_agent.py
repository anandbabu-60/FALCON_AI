from typing import List, Optional

from app.services.resource_recommender import recommend_datasets
from app.services.tool_recommender import recommend_tools


class GapAgent:
    """
    Coordinates resource recommendations based on
    identified research gaps.

    Responsibilities:
    1. Recommend suitable datasets.
    2. Recommend suitable research tools.
    """

    def recommend_datasets(
        self,
        research_topic: str,
        research_gaps: List[str],
        methodology: str,
        evidence: Optional[List[dict]] = None
    ):
        return recommend_datasets(
            research_topic=research_topic,
            research_gaps=research_gaps,
            methodology=methodology,
            evidence=evidence
        )

    def recommend_tools(
        self,
        research_topic: str,
        research_gaps: List[str],
        methodology: str,
        evidence: Optional[List[dict]] = None
    ):
        return recommend_tools(
            research_topic=research_topic,
            research_gaps=research_gaps,
            methodology=methodology,
            evidence=evidence
        )

    def run(
        self,
        research_topic: str,
        research_gaps: List[str],
        evidence: Optional[List[dict]] = None
    ):
        """
        Run the resource recommendation stage.
        """

        methodology = (
            "Use the identified research gaps to recommend "
            "appropriate research resources."
        )

        dataset_recommendations = self.recommend_datasets(
            research_topic=research_topic,
            research_gaps=research_gaps,
            methodology=methodology,
            evidence=evidence
        )

        tool_recommendations = self.recommend_tools(
            research_topic=research_topic,
            research_gaps=research_gaps,
            methodology=methodology,
            evidence=evidence
        )

        return {
            "dataset_recommendations":
                dataset_recommendations,

            "tool_recommendations":
                tool_recommendations
        }