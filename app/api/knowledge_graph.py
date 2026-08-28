import uuid
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.integrations.neo4j import add_research_gap, add_theme, get_project_graph, initialize_schema, is_configured, upsert_paper, upsert_project, verify_connection
from app.models.research import LiteraturePaper, ResearchGap
from app.services.projects import get_owned_project
from app.services.resources import get_resource

router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])


class ProjectRequest(BaseModel):
    project_id: uuid.UUID
    title: str = Field(min_length=2, max_length=500)
    description: str | None = None


class PaperRequest(BaseModel):
    project_id: uuid.UUID
    paper_id: uuid.UUID
    title: str = Field(min_length=2, max_length=1000)
    authors: str | None = None
    abstract: str | None = None


class ThemeRequest(BaseModel):
    project_id: uuid.UUID
    paper_id: uuid.UUID
    theme: str = Field(min_length=2, max_length=255)


class GapRequest(BaseModel):
    project_id: uuid.UUID
    gap_title: str = Field(min_length=2, max_length=500)


@router.get("/health")
def neo4j_health():
    if not is_configured():
        return {"configured": False, "connected": False, "message": "Neo4j environment variables are not configured."}
    try:
        return {"configured": True, **verify_connection()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": "Neo4j connection failed", "message": str(exc)}) from exc


@router.post("/initialize")
def initialize_knowledge_graph(_: CurrentUser):
    if not is_configured():
        raise HTTPException(status_code=503, detail="Neo4j is not configured.")
    try:
        return initialize_schema()
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": "Neo4j initialization failed", "message": str(exc)}) from exc


@router.post("/project")
def create_project_node(request: ProjectRequest, current_user: CurrentUser, db: DBSession):
    get_owned_project(db, request.project_id, current_user.id)
    try:
        return upsert_project(str(request.project_id), request.title, request.description)
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": "Failed to create project graph node", "message": str(exc)}) from exc


@router.post("/paper")
def create_paper_node(request: PaperRequest, current_user: CurrentUser, db: DBSession):
    get_resource(db, LiteraturePaper, request.project_id, request.paper_id, current_user.id)
    try:
        return upsert_paper(str(request.project_id), str(request.paper_id), request.title, request.authors, request.abstract)
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": "Failed to create paper graph node", "message": str(exc)}) from exc


@router.post("/theme")
def create_theme_edge(request: ThemeRequest, current_user: CurrentUser, db: DBSession):
    get_resource(db, LiteraturePaper, request.project_id, request.paper_id, current_user.id)
    try:
        result = add_theme(str(request.paper_id), request.theme)
        if result is None:
            raise HTTPException(status_code=404, detail="Paper not found in knowledge graph.")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": "Failed to create theme relationship", "message": str(exc)}) from exc


@router.post("/gap")
def create_gap_edge(request: GapRequest, current_user: CurrentUser, db: DBSession):
    get_owned_project(db, request.project_id, current_user.id)
    try:
        result = add_research_gap(str(request.project_id), request.gap_title)
        if result is None:
            raise HTTPException(status_code=404, detail="Project not found in knowledge graph.")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": "Failed to create research-gap relationship", "message": str(exc)}) from exc


@router.get("/project/{project_id}")
def project_graph(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    get_owned_project(db, project_id, current_user.id)
    try:
        result = get_project_graph(str(project_id))
        if result is None:
            raise HTTPException(status_code=404, detail="Project not found in knowledge graph.")
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": "Failed to read knowledge graph", "message": str(exc)}) from exc


@router.post("/project/{project_id}/sync")
def sync_project_graph(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    """Build graph concepts from the project's relational research records."""
    project = get_owned_project(db, project_id, current_user.id)
    if not is_configured():
        raise HTTPException(status_code=503, detail="Neo4j is not configured. Set NEO4J_URI, NEO4J_USERNAME and NEO4J_PASSWORD.")
    try:
        upsert_project(str(project.id), project.title, project.description)
        papers = db.scalars(select(LiteraturePaper).where(LiteraturePaper.project_id == project.id).limit(100)).all()
        for paper in papers:
            upsert_paper(str(project.id), str(paper.id), paper.title, paper.authors, paper.abstract)
            keywords = [part.strip() for part in (paper.keywords or "").split(",") if part.strip()]
            if not keywords:
                keywords = [word for word in re.findall(r"[A-Za-z][A-Za-z-]{4,}", paper.title)[:3]]
            for theme in keywords[:5]:
                add_theme(str(paper.id), theme)
        for gap in db.scalars(select(ResearchGap).where(ResearchGap.project_id == project.id).limit(100)).all():
            add_research_gap(str(project.id), gap.research_gap)
        return {"synced": True, "papers": len(papers), "gaps": len(db.scalars(select(ResearchGap).where(ResearchGap.project_id == project.id)).all()), "graph": get_project_graph(str(project.id))}
    except Exception as exc:
        raise HTTPException(status_code=503, detail={"error": "Failed to synchronize project graph", "message": str(exc)}) from exc
