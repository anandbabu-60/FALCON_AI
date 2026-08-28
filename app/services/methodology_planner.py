from typing import List, Optional

from pydantic import BaseModel

from app.integrations.gemini import generate_content


class MethodologyRecommendation(BaseModel):
    methodology_name: str
    research_design: str
    recommended_methods: List[str]
    data_requirements: List[str]
    evaluation_strategy: List[str]
    strengths: List[str]
    limitations: List[str]
    suitability: str


class MethodologyRecommendationResponse(BaseModel):
    recommendations: List[MethodologyRecommendation]


def recommend_methodology(
    research_topic: str,
    research_gaps: List[str],
    available_datasets: List[str],
    available_tools: List[str],
    evidence: Optional[List[dict]] = None
) -> MethodologyRecommendationResponse:

    # ========================================================
    # Research gaps
    # ========================================================

    gaps_text = "\n".join(
        f"- {gap}"
        for gap in research_gaps
    )

    # ========================================================
    # Available datasets
    # ========================================================

    datasets_text = "\n".join(
        f"- {dataset}"
        for dataset in available_datasets
    )

    # ========================================================
    # Available tools
    # ========================================================

    tools_text = "\n".join(
        f"- {tool}"
        for tool in available_tools
    )

    # ========================================================
    # Retrieved evidence
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
You are an academic research methodology advisor.

Research topic:
{research_topic}

============================================================
IDENTIFIED RESEARCH GAPS
============================================================

{gaps_text}

============================================================
AVAILABLE DATASETS
============================================================

{datasets_text}

============================================================
AVAILABLE TOOLS
============================================================

{tools_text}

============================================================
RETRIEVED RESEARCH EVIDENCE
============================================================

{evidence_text}

============================================================
TASK
============================================================

Recommend suitable research methodologies for this study.

For every methodology provide:

1. Methodology name
2. Research design
3. Recommended methods
4. Data requirements
5. Evaluation strategy
6. Strengths
7. Limitations
8. Suitability

============================================================
RULES
============================================================

- Base recommendations on the provided research topic,
  gaps, datasets, tools, and evidence.
- Do not invent datasets or tools.
- Do not claim that a methodology guarantees success.
- Explain why the methodology fits the research problem.
- Use retrieved evidence when it is relevant.
- Do not treat retrieved evidence as proof that a methodology
  will succeed.
- Clearly distinguish evidence-supported reasoning from
  general methodological knowledge.
- If information is unavailable, say "Not specified".
- Keep the analysis academically useful and concise.
"""

    return generate_content(
        prompt=prompt,
        response_schema=MethodologyRecommendationResponse,
    )