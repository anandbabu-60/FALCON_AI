from typing import List, Optional

from pydantic import BaseModel

from app.integrations.gemini import generate_content


class ToolRecommendation(BaseModel):
    name: str
    purpose: str
    relevance: str
    category: str | None = None
    official_website: str | None = None
    license: str | None = None
    strengths: List[str]
    limitations: List[str]
    suitability: str


class ToolRecommendationResponse(BaseModel):
    recommendations: List[ToolRecommendation]


def recommend_tools(
    research_topic: str,
    research_gaps: List[str],
    methodology: str,
    evidence: Optional[List[dict]] = None
) -> ToolRecommendationResponse:

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
You are an academic research assistant helping researchers
select appropriate software and research tools.

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

Recommend suitable research tools, software libraries,
platforms, or frameworks that can help conduct this research.

For every tool provide:

1. Tool name
2. Purpose
3. Why it is relevant to the research
4. Strengths
5. Limitations
6. Suitability
7. Category, official website, and license (or "Not specified")

============================================================
IMPORTANT RULES
============================================================

- Recommend only real, known tools or software.
- Prefer the official project website or documentation URL.
- Never fabricate a URL. Use null or "Not specified" when it cannot be
  verified from the supplied context.
- Do not invent tool names.
- Do not invent capabilities.
- If information is unavailable, say "Not specified".
- Do not claim that a tool guarantees better research
  results.
- Consider the research topic, methodology, and identified
  gaps.
- Use the retrieved evidence when it is relevant.
- Do not treat retrieved evidence as proof that a tool is
  suitable.
- Clearly distinguish evidence-supported reasoning from
  general knowledge.
- Keep the recommendations concise and academically useful.
"""

    return generate_content(
        prompt=prompt,
        response_schema=ToolRecommendationResponse,
    )
