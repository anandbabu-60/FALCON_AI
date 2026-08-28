import json
import uuid
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.research import Dataset, ExperimentPlan, ResearchGap, RoadmapEntry, ToolRecommendation


def materialize_workflow(db: Session, project_id: uuid.UUID, result: dict[str, Any]) -> dict[str, int]:
    """Save structured workflow output as editable project resources.

    The AI response remains available as an immutable AI artifact; these rows
    give students editable gaps, resources, experiments, and milestones.
    """
    result = jsonable_encoder(result)
    counts = {"gaps": 0, "datasets": 0, "tools": 0, "experiments": 0, "roadmap": 0}
    gap_analysis = result.get("gap_analysis") or {}
    for item in gap_analysis.get("gaps", []):
        db.add(ResearchGap(project_id=project_id, problem=item.get("observation") or item.get("gap_title") or "Potential research problem", existing_solution=None, limitation=item.get("evidence", [None])[0] if item.get("evidence") else None, research_gap=item.get("gap_title") or "Potential research gap", proposed_innovation=item.get("potential_direction")))
        counts["gaps"] += 1
    for item in (result.get("dataset_recommendations") or {}).get("recommendations", []):
        db.add(Dataset(project_id=project_id, name=item.get("name") or "Recommended dataset", description=item.get("purpose") or item.get("relevance"), source=item.get("source"), download_link=item.get("download_link"), license=item.get("license"), size=item.get("size"), domain=item.get("domain")))
        counts["datasets"] += 1
    for item in (result.get("tool_recommendations") or {}).get("recommendations", []):
        db.add(ToolRecommendation(project_id=project_id, name=item.get("name") or "Recommended tool", category=item.get("category"), official_website=item.get("official_website"), description=item.get("purpose") or item.get("relevance"), license=item.get("license")))
        counts["tools"] += 1
    def lines(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, list):
            return "\n".join(str(item) for item in value)
        return str(value)

    methodology = result.get("methodology_recommendations") or {}
    experiment = result.get("experiment_plan") or {}
    if methodology or experiment:
        db.add(ExperimentPlan(project_id=project_id, methodology=json.dumps(methodology), algorithms=lines(experiment.get("baseline_models", []) + experiment.get("proposed_models", [])), evaluation_metrics=lines(experiment.get("evaluation_metrics", [])), workflow=lines(experiment.get("experiments", [])), expected_results=lines(experiment.get("expected_outputs", []) or experiment.get("expected_results", []))))
        counts["experiments"] = 1
    week = 1
    for phase in (result.get("roadmap") or {}).get("phases", []):
        for task in phase.get("tasks", []):
            db.add(RoadmapEntry(project_id=project_id, week_number=week, task=task, status="pending", remarks=phase.get("objective")))
            counts["roadmap"] += 1
            week += 1
    db.commit()
    return counts
