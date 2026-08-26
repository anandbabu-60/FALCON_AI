import os
from typing import List, Optional

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=api_key)


# ============================================================
# Response Models
# ============================================================

class ResearchGap(BaseModel):
    gap_title: str
    observation: str
    evidence: List[str]
    potential_direction: str
    confidence: str


class GapAnalysis(BaseModel):
    gaps: List[ResearchGap]
    overall_research_direction: str


# ============================================================
# Research Gap Analysis
# ============================================================

def analyze_research_gaps(
    research_topic: str,
    paper_analyses: List[str],
    theme_analysis: str,
    evidence: Optional[List[dict]] = None
) -> GapAnalysis:

    # --------------------------------------------------------
    # Paper analyses
    # --------------------------------------------------------

    papers_text = "\n\n".join(
        f"Paper Analysis {i + 1}:\n{paper}"
        for i, paper in enumerate(paper_analyses)
    )

    # --------------------------------------------------------
    # Retrieved RAG evidence
    # --------------------------------------------------------

    if evidence:

        evidence_parts = []

        for item in evidence:

            evidence_id = item.get("id", "Unknown")
            source = item.get("source", "Unknown")
            page = item.get("page", "Unknown")
            text = item.get("text", "")

            evidence_parts.append(
                f"""
[Evidence {evidence_id}]
Source: {source}
Page: {page}

{text}
"""
            )

        evidence_text = "\n".join(evidence_parts)

    else:

        evidence_text = (
            "No additional retrieved research evidence "
            "was provided."
        )

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are an expert academic research advisor.

Your task is to identify POTENTIAL research gaps or
underexplored directions from the supplied research
information.

Research topic:
{research_topic}

============================================================
RESEARCH THEMES
============================================================

{theme_analysis}

============================================================
PAPER ANALYSES
============================================================

{papers_text}

============================================================
RETRIEVED RESEARCH EVIDENCE
============================================================

{evidence_text}

============================================================
TASK
============================================================

Identify potential research gaps or underexplored
directions.

For each potential gap provide:

1. Gap title
2. Observation
3. Evidence from the supplied information
4. Potential research direction
5. Confidence level:
   Low, Moderate, or High

============================================================
IMPORTANT ACADEMIC RULES
============================================================

- Base conclusions ONLY on the supplied information.
- Use the paper analyses and retrieved evidence together.
- Do not invent papers, statistics, datasets, or findings.
- Do not claim that a gap is definitely novel.
- Do not say "no previous research exists".
- A limitation mentioned by one paper is not automatically
  a research gap.
- Clearly distinguish observations from potential gaps.
- Use cautious academic language.
- If evidence is insufficient, explicitly say so.
- Do not treat retrieved evidence as proof of novelty.
- Do not make claims that cannot be supported by the supplied
  paper analyses or retrieved evidence.
- When possible, identify which supplied evidence supports
  the observation.
- Confidence must reflect the strength of the supplied
  evidence, not the model's general knowledge.

Finally provide one overall potential research direction.
"""

    # --------------------------------------------------------
    # Gemini
    # --------------------------------------------------------

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": GapAnalysis,
        },
    )

    return response.parsed