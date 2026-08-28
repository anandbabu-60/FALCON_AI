from typing import List, Optional

from app.services.gap_analyzer import analyze_research_gaps


class AnalysisAgent:
    """
    Coordinates research analysis after literature analysis.

    Responsibility:
    Identify potential research gaps using:

    - paper analyses
    - research themes
    - retrieved research evidence
    """

    def analyze_gaps(
        self,
        research_topic: str,
        paper_analyses: List[str],
        theme_analysis: str,
        evidence: Optional[List[dict]] = None
    ):
        return analyze_research_gaps(
            research_topic=research_topic,
            paper_analyses=paper_analyses,
            theme_analysis=theme_analysis,
            evidence=evidence
        )

    def run(
        self,
        research_topic: str,
        paper_analyses: List[str],
        theme_analysis: str,
        evidence: Optional[List[dict]] = None
    ):
        """
        Run the research-gap analysis stage.
        """

        return self.analyze_gaps(
            research_topic=research_topic,
            paper_analyses=paper_analyses,
            theme_analysis=theme_analysis,
            evidence=evidence
        )