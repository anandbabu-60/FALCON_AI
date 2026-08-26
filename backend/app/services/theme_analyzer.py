from typing import List

from pydantic import BaseModel

from app.integrations.gemini import generate_content


class ThemeAnalysis(BaseModel):
    common_research_themes: List[str]
    common_methods: List[str]
    common_datasets: List[str]
    common_techniques: List[str]
    emerging_directions: List[str]
    major_differences: List[str]


def analyze_research_themes(papers: List[str]) -> ThemeAnalysis:

    papers_text = "\n\n".join(
        f"Paper {i + 1}:\n{paper}"
        for i, paper in enumerate(papers)
    )

    prompt = f"""
You are an expert academic research analyst.

Analyze the following collection of research papers.

{papers_text}

Identify:

1. Common research themes
2. Common methodologies or methods
3. Common datasets
4. Common techniques or models
5. Emerging research directions
6. Major differences between the papers

Rules:

- Base your analysis ONLY on the information provided.
- Do not invent papers, datasets, methods, or results.
- If information is unavailable, say "Not specified".
- Do not claim that an identified direction is definitely a research gap.
- Return concise but useful academic analysis.
"""

    return generate_content(
        prompt=prompt,
        response_schema=ThemeAnalysis,
    )