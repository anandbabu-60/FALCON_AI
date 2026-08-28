from typing import List

from app.services.paper_analyzer import analyze_paper
from app.services.theme_analyzer import ThemeAnalysis, analyze_research_themes


class LiteratureAgent:
    """
    Coordinates literature analysis.

    Responsibilities:
    1. Analyze individual research papers.
    2. Identify common themes across the analyzed papers.
    """

    def analyze_papers(self, papers: List[dict]):
        """
        Analyze a collection of papers.

        Each paper must contain:
        - title
        - abstract
        """

        paper_analyses = []

        for paper in papers:
            analysis = analyze_paper(
                title=paper["title"],
                abstract=paper["abstract"]
            )

            paper_analyses.append(analysis)

        return paper_analyses

    def analyze_themes(self, paper_analyses):
        """
        Analyze common themes across paper analyses.
        """

        papers_text = [
            analysis.model_dump_json()
            for analysis in paper_analyses
        ]

        return analyze_research_themes(papers_text)

    def run(self, papers: List[dict]):
        """
        Run the complete literature-analysis stage.
        """

        # A student should be able to create an initial AI roadmap before
        # manually saving papers.  Keep the workflow honest in that case by
        # returning explicit "not specified" literature fields instead of
        # pretending that paper evidence exists.
        if not papers:
            return {
                "paper_analyses": [],
                "theme_analysis": ThemeAnalysis(
                    common_research_themes=["Not specified — add papers to refine this analysis"],
                    common_methods=["Not specified"],
                    common_datasets=["Not specified"],
                    common_techniques=["Not specified"],
                    emerging_directions=["Not specified"],
                    major_differences=["No saved papers were supplied"],
                ),
            }

        paper_analyses = self.analyze_papers(papers)

        theme_analysis = self.analyze_themes(
            paper_analyses
        )

        return {
            "paper_analyses": paper_analyses,
            "theme_analysis": theme_analysis
        }
