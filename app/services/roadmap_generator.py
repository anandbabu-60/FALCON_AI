from typing import List, Optional

from pydantic import BaseModel

from app.integrations.gemini import generate_content


class RoadmapPhase(BaseModel):
    phase_name: str
    objective: str
    tasks: List[str]
    deliverables: List[str]
    milestones: List[str]


class ResearchRoadmap(BaseModel):
    research_goal: str
    phases: List[RoadmapPhase]
    final_deliverables: List[str]


def generate_roadmap(
    research_topic: str,
    research_gaps: List[str],
    methodology: str,
    experiment_plan: str,
    evidence: Optional[List[dict]] = None
) -> ResearchRoadmap:

    # ========================================================
    # Research gaps
    # ========================================================

    gaps_text = "\n".join(
        f"- {gap}"
        for gap in research_gaps
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
You are an expert academic research project planner.

Research topic:
{research_topic}

============================================================
POTENTIAL RESEARCH GAPS
============================================================

{gaps_text}

============================================================
PROPOSED METHODOLOGY
============================================================

{methodology}

============================================================
EXPERIMENT PLAN
============================================================

{experiment_plan}

============================================================
RETRIEVED RESEARCH EVIDENCE
============================================================

{evidence_text}

============================================================
TASK
============================================================

Create a practical research roadmap.

The roadmap should include:

1. Overall research goal
2. Research phases
3. Objective for each phase
4. Tasks for each phase
5. Deliverables for each phase
6. Milestones for each phase
7. Final research deliverables

============================================================
RULES
============================================================

- Base the roadmap on the provided information.
- Use retrieved evidence when it is relevant.
- Do not invent datasets, tools, models, or results.
- Do not claim that any research outcome is guaranteed.
- Do not treat retrieved evidence as proof that the
  proposed research will succeed.
- Keep the roadmap realistic and academically useful.
- If information is unavailable, say "Not specified".
"""

    return generate_content(
        prompt=prompt,
        response_schema=ResearchRoadmap,
    )