import os
from typing import List

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


class ResearchGap(BaseModel):
    gap_title: str
    observation: str
    evidence: List[str]
    potential_direction: str
    confidence: str


class GapAnalysis(BaseModel):
    gaps: List[ResearchGap]
    overall_research_direction: str


def analyze_research_gaps(
    research_topic: str,
    paper_analyses: List[str],
    theme_analysis: str
) -> GapAnalysis:

    papers_text = "\n\n".join(
        f"Paper Analysis {i + 1}:\n{paper}"
        for i, paper in enumerate(paper_analyses)
    )

    prompt = f"""
You are an expert academic research advisor.

Your task is to identify POTENTIAL research gaps or
underexplored directions from the provided evidence.

Research topic:
{research_topic}

Research themes:
{theme_analysis}

Paper analyses:
{papers_text}

For each potential gap provide:

1. Gap title
2. Observation
3. Evidence from the provided papers
4. Potential research direction
5. Confidence level: Low, Moderate, or High

IMPORTANT ACADEMIC RULES:

- Base conclusions ONLY on the supplied information.
- Do not invent papers, statistics, datasets, or findings.
- Do not claim that a gap is definitely novel.
- Do not say "no previous research exists".
- A limitation mentioned by one paper is not automatically a
  research gap.
- Clearly distinguish observations from potential research gaps.
- Use cautious academic language.
- If evidence is insufficient, say so.

Finally provide one overall potential research direction.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GapAnalysis,
        },
    )

    return response.parsed
