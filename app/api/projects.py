import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Query, Response, status
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DBSession
from app.models.project import ProjectStatus, ResearchProject
from app.models.research import Dataset, LiteraturePaper, ResearchGap, RoadmapEntry, RoadmapStatus
from app.repositories.base import BaseRepository
from app.schemas.common import Page
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.research import RoadmapResponse
from app.services.projects import get_owned_project, list_owned_projects

router = APIRouter(prefix="/projects", tags=["Research Projects"])
repository = BaseRepository(ResearchProject)


def _roadmap_plan(project: ResearchProject, paper_count: int, dataset_count: int, gap_count: int, paper_titles: list[str] | None = None) -> list[tuple[int, str, str]]:
    """Build a project-specific roadmap from its topic and saved evidence."""
    text = f"{project.title} {project.research_idea} {project.domain or ''}".lower()
    titles = [title for title in (paper_titles or []) if title]
    source_note = f"Analyzes {paper_count} saved paper link(s)" + (f", including: {titles[0][:120]}." if titles else ". Gather papers to add project evidence.")
    if any(word in text for word in ("plant", "crop", "leaf", "disease", "vision", "image")):
        tasks = [
            "Define the field plant-disease classes, research question, and success criteria.",
            "Review the saved plant-vision papers and document field-vs-laboratory evidence.",
            f"Prepare image datasets and annotation protocol ({dataset_count} saved dataset recommendation(s)).",
            "Implement and reproduce a lightweight CNN or vision-transformer baseline.",
            "Design domain-adaptation and explainability experiments for changing field conditions.",
            "Evaluate precision, recall, F1, calibration, and cross-condition generalization.",
            f"Run ablations and error analysis against the {gap_count} saved research gap(s).",
            "Validate representative field cases and finalize the thesis report with supervisor feedback.",
        ]
    elif any(word in text for word in ("federated", "intrusion", "cyber", "network", "iot", "security")):
        tasks = [
            "Define the IoT threat model, privacy assumptions, research question, and success criteria.",
            "Compare saved cybersecurity papers and map their datasets, attack classes, and limitations.",
            f"Prepare traffic partitions and client simulation using {dataset_count} saved dataset recommendation(s).",
            "Implement a centralized intrusion-detection baseline and establish reproducible metrics.",
            "Implement federated aggregation and privacy controls under realistic client heterogeneity.",
            "Evaluate detection quality, communication cost, convergence, and privacy trade-offs.",
            f"Run attack, ablation, and robustness analysis against the {gap_count} saved research gap(s).",
            "Review findings with the supervisor and finalize deployment notes, citations, and thesis report.",
        ]
    elif any(word in text for word in ("nlp", "language", "text", "sentiment", "translation", "summarization")):
        tasks = [
            "Define the language task, research question, target population, and evaluation criteria.",
            "Synthesize the saved NLP papers into a methods, datasets, and limitations matrix.",
            f"Prepare the corpus, preprocessing, and data-split protocol ({dataset_count} saved dataset recommendation(s)).",
            "Reproduce a classical and transformer baseline with fixed training and evaluation seeds.",
            "Develop the proposed low-resource, multilingual, or domain-adaptation method.",
            "Evaluate task metrics, robustness, fairness, and error categories across test slices.",
            f"Run ablations and qualitative error analysis for the {gap_count} saved research gap(s).",
            "Review results with the supervisor and finalize the reproducible thesis package.",
        ]
    else:
        tasks = [
            f"Define the research question, scope, and success criteria for {project.title}.",
            "Review saved papers and extract methods, datasets, baselines, and evidence limitations.",
            f"Select and document datasets, tools, baselines, and evaluation metrics ({dataset_count} dataset recommendation(s)).",
            "Implement a reproducible baseline and record the complete experiment environment.",
            "Implement the proposed method and define a fair comparison protocol.",
            "Evaluate results, uncertainty, limitations, and reproducibility across agreed metrics.",
            f"Run ablations and gap-focused error analysis against the {gap_count} saved research gap(s).",
            "Review findings with the supervisor and finalize citations, report, and next milestones.",
        ]
    return [(week, task, source_note if week == 2 else "Update this milestone with notes, links, and supervisor feedback.") for week, task in enumerate(tasks, start=1)]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, current_user: CurrentUser, db: DBSession):
    project = repository.create(db, {**payload.model_dump(), "owner_id": current_user.id})
    # Every new workspace starts with an actionable M.Tech research scaffold.
    # Gemini can later enrich this with project-specific milestones.
    # Keep the initial workspace lightweight; opening Roadmap later expands it
    # to the full eight-week project-specific plan after evidence is gathered.
    for week, task, remarks in _roadmap_plan(project, 0, 0, 0)[:4]:
        db.add(RoadmapEntry(project_id=project.id, week_number=week, task=task, deadline=date.today() + timedelta(days=week * 7), status=RoadmapStatus.in_progress if week == 1 else RoadmapStatus.pending, remarks=remarks))
    db.commit()
    db.refresh(project)
    # Keep Neo4j optional: a missing graph service must never block the
    # relational project workflow.
    try:
        from app.integrations.neo4j import is_configured, upsert_project
        if is_configured():
            upsert_project(str(project.id), project.title, project.description)
    except Exception:
        pass
    return project


@router.post("/{project_id}/roadmap/generate", response_model=list[RoadmapResponse])
def generate_project_roadmap(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    """Create an actionable roadmap from the project's current evidence.

    This deterministic baseline works even when Gemini is unavailable. AI
    workflow generation can enrich the same roadmap later without leaving a
    newly-created project empty.
    """
    project = get_owned_project(db, project_id, current_user.id)
    saved_papers = db.scalars(select(LiteraturePaper).where(LiteraturePaper.project_id == project.id).order_by(LiteraturePaper.created_at.asc()).limit(20)).all()
    paper_count = len(saved_papers)
    dataset_count = db.scalar(select(func.count(Dataset.id)).where(Dataset.project_id == project.id)) or 0
    gap_count = db.scalar(select(func.count(ResearchGap.id)).where(ResearchGap.project_id == project.id)) or 0
    tasks = {week: (task, remarks) for week, task, remarks in _roadmap_plan(project, paper_count, dataset_count, gap_count, [paper.title for paper in saved_papers])}
    existing = {entry.week_number: entry for entry in db.scalars(select(RoadmapEntry).where(RoadmapEntry.project_id == project.id)).all()}
    if existing.get(1) and existing[1].status == RoadmapStatus.pending:
        existing[1].status = RoadmapStatus.in_progress
    for week, (task, remarks) in tasks.items():
        if week in existing:
            existing[week].task = task
            existing[week].remarks = remarks
        else:
            db.add(RoadmapEntry(project_id=project.id, week_number=week, task=task, deadline=date.today() + timedelta(days=week * 7), status=RoadmapStatus.pending, remarks=remarks))
    db.commit()
    return db.scalars(select(RoadmapEntry).where(RoadmapEntry.project_id == project.id).order_by(RoadmapEntry.week_number.asc())).all()


@router.get("/{project_id}/roadmap/reminders")
def roadmap_reminders(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    """Return actionable in-app reminders for unfinished roadmap work."""
    project = get_owned_project(db, project_id, current_user.id)
    today = date.today()
    entries = db.scalars(select(RoadmapEntry).where(RoadmapEntry.project_id == project.id, RoadmapEntry.status != RoadmapStatus.completed, RoadmapEntry.deadline.is_not(None), RoadmapEntry.deadline <= today + timedelta(days=3)).order_by(RoadmapEntry.deadline.asc())).all()
    reminders = []
    for entry in entries:
        days = (today - entry.deadline).days if entry.deadline else 0
        if days > 0:
            message = f"Deadline passed for Week {entry.week_number}: {entry.task}"
            kind = "overdue"
        elif days == 0:
            message = f"Deadline is today for Week {entry.week_number}: {entry.task}"
            kind = "due_today"
        else:
            message = f"Week {entry.week_number} is due in {abs(days)} day(s): {entry.task}"
            kind = "upcoming"
        reminders.append({"id": str(entry.id), "project_id": str(project.id), "week_number": entry.week_number, "task": entry.task, "deadline": entry.deadline, "status": entry.status, "kind": kind, "message": message})
    return {"items": reminders, "total": len(reminders)}


@router.get("", response_model=Page[ProjectResponse])
def list_projects(current_user: CurrentUser, db: DBSession, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), search: str | None = None, domain: str | None = None, project_status: ProjectStatus | None = None):
    items, total = list_owned_projects(db, current_user.id, page, size, search, domain, project_status)
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession): return get_owned_project(db, project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: uuid.UUID, payload: ProjectUpdate, current_user: CurrentUser, db: DBSession):
    return repository.update(db, get_owned_project(db, project_id, current_user.id), payload.model_dump(exclude_unset=True))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    repository.delete(db, get_owned_project(db, project_id, current_user.id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
