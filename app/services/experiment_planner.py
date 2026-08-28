from typing import List, Optional

from pydantic import BaseModel

from app.integrations.gemini import generate_content


class ExperimentPlan(BaseModel):
    research_question: str
    hypothesis: str
    datasets: List[str]
    preprocessing_steps: List[str]
    baseline_models: List[str]
    proposed_models: List[str]
    experiments: List[str]
    evaluation_metrics: List[str]
    ablation_studies: List[str]
    expected_outputs: List[str]


def plan_experiments(
    research_topic: str,
    research_gaps: List[str],
    methodology: str,
    datasets: List[str],
    tools: List[str],
    evidence: Optional[List[dict]] = None
) -> ExperimentPlan:

    # ========================================================
    # Research gaps
    # ========================================================

    gaps_text = "\n".join(
        f"- {gap}"
        for gap in research_gaps
    )

    # ========================================================
    # Datasets
    # ========================================================

    datasets_text = "\n".join(
        f"- {dataset}"
        for dataset in datasets
    )

    # ========================================================
    # Tools
    # ========================================================

    tools_text = "\n".join(
        f"- {tool}"
        for tool in tools
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
You are an expert research experiment planner.

Research topic:
{research_topic}

============================================================
RESEARCH GAPS
============================================================

{gaps_text}

============================================================
PROPOSED METHODOLOGY
============================================================

{methodology}

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

Design a concrete experimental plan for this research.

Include:

1. Research question
2. Hypothesis
3. Datasets
4. Preprocessing steps
5. Baseline models
6. Proposed models
7. Experiments
8. Evaluation metrics
9. Ablation studies
10. Expected outputs

============================================================
RULES
============================================================

- Base the plan on the provided information.
- Do not invent datasets or tools.
- Do not claim that the hypothesis is proven.
- Use retrieved evidence when relevant.
- Do not treat retrieved evidence as proof that an
  experiment will succeed.
- Keep the experimental design realistic and
  academically useful.
- If information is unavailable, say "Not specified".
- Clearly distinguish evidence-supported decisions from
  general experimental best practices.
"""

    return generate_content(
        prompt=prompt,
        response_schema=ExperimentPlan,
    )