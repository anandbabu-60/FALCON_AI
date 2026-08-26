from typing import List, Optional

from pydantic import BaseModel

from app.integrations.gemini import generate_content


class DatasetRecommendation(BaseModel):
    name: str
    purpose: str
    relevance: str
    strengths: List[str]
    limitations: List[str]
    suitability: str
    evidence: List[str]


class DatasetRecommendationResponse(BaseModel):
    recommendations: List[DatasetRecommendation]


def recommend_datasets(
    research_topic: str,
    research_gaps: List[str],
    methodology: str,
    evidence: Optional[List[dict]] = None
) -> DatasetRecommendationResponse:

    # ========================================================
    # Research gaps
    # ========================================================

    gaps_text = "\n".join(
        f"- {gap}"
        for gap in research_gaps
    )

    # ========================================================
    # Retrieved research evidence
    # ========================================================

    if evidence:

        evidence_parts = []

        for item in evidence:

            evidence_id = item.get(
                "id",
                "Unknown"
            )

            source = item.get(
                "source",
                "Unknown"
            )

            page = item.get(
                "page",
                "Unknown"
            )

            text = item.get(
                "text",
                ""
            )

            evidence_parts.append(
                f"""
[Evidence {evidence_id}]
Source: {source}
Page: {page}

{text}
"""
            )

        evidence_text = "\n".join(
            evidence_parts
        )

    else:

        evidence_text = (
            "No retrieved research evidence was provided."
        )

    # ========================================================
    # Prompt
    # ========================================================

    prompt = f"""
You are an academic research assistant specializing in
dataset selection.

Research topic:
{research_topic}

============================================================
IDENTIFIED RESEARCH GAPS
============================================================

{gaps_text}

============================================================
PROPOSED METHODOLOGY
============================================================

{methodology}

============================================================
RETRIEVED RESEARCH EVIDENCE
============================================================

{evidence_text}

============================================================
TASK
============================================================

Recommend suitable datasets for this research.

For every dataset provide:

1. Dataset name
2. Purpose
3. Why it is relevant to the research
4. Strengths
5. Limitations
6. Suitability
7. Evidence supporting the recommendation

============================================================
EVIDENCE GROUNDING RULES
============================================================

- Recommend only datasets that are known to exist.
- Do not invent dataset names.
- Do not invent dataset properties.
- If a property is uncertain, say "Not specified".
- Use the supplied research evidence when it supports
  the recommendation.
- Do not pretend that general model knowledge came from
  the supplied evidence.
- Do not invent evidence numbers.
- For the "evidence" field, use references such as:
  "Evidence 1"
  "Evidence 2"
- If the supplied research evidence does not directly
  support the dataset recommendation, write:
  "No direct evidence in supplied research."
- A dataset may still be recommended based on general
  academic knowledge, but this must not be presented as
  retrieved evidence.
- Explain why each dataset fits the research problem.
- Consider the identified research gaps.
- Keep the recommendations academically useful.
"""

    return generate_content(
        prompt=prompt,
        response_schema=DatasetRecommendationResponse,
    )