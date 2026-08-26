from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.integrations.neo4j import (
    is_configured,
    verify_connection,
    initialize_schema,
    upsert_project,
    upsert_paper,
    add_theme,
    add_research_gap,
    get_project_graph,
)


router = APIRouter(
    prefix="/knowledge-graph",
    tags=["Knowledge Graph"],
)


class ProjectRequest(BaseModel):
    project_id: int
    title: str
    description: str | None = None


class PaperRequest(BaseModel):
    project_id: int
    paper_id: int
    title: str
    authors: str | None = None
    abstract: str | None = None


class ThemeRequest(BaseModel):
    paper_id: int
    theme: str


class GapRequest(BaseModel):
    project_id: int
    gap_title: str


@router.get("/health")
def neo4j_health():
    if not is_configured():
        return {
            "configured": False,
            "connected": False,
            "message": "Neo4j environment variables are not configured.",
        }

    try:
        return {
            "configured": True,
            **verify_connection(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Neo4j connection failed",
                "message": str(exc),
            },
        )


@router.post("/initialize")
def initialize_knowledge_graph():
    if not is_configured():
        raise HTTPException(
            status_code=503,
            detail="Neo4j is not configured.",
        )

    try:
        return initialize_schema()

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Neo4j initialization failed",
                "message": str(exc),
            },
        )


@router.post("/project")
def create_project_node(request: ProjectRequest):
    try:
        return upsert_project(
            project_id=request.project_id,
            title=request.title,
            description=request.description,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Failed to create project graph node",
                "message": str(exc),
            },
        )


@router.post("/paper")
def create_paper_node(request: PaperRequest):
    try:
        return upsert_paper(
            project_id=request.project_id,
            paper_id=request.paper_id,
            title=request.title,
            authors=request.authors,
            abstract=request.abstract,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Failed to create paper graph node",
                "message": str(exc),
            },
        )


@router.post("/theme")
def create_theme_edge(request: ThemeRequest):
    try:
        result = add_theme(
            paper_id=request.paper_id,
            theme=request.theme,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Paper not found in knowledge graph.",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Failed to create theme relationship",
                "message": str(exc),
            },
        )


@router.post("/gap")
def create_gap_edge(request: GapRequest):
    try:
        result = add_research_gap(
            project_id=request.project_id,
            gap_title=request.gap_title,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found in knowledge graph.",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Failed to create research-gap relationship",
                "message": str(exc),
            },
        )


@router.get("/project/{project_id}")
def project_graph(project_id: int):
    try:
        result = get_project_graph(project_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Project not found in knowledge graph.",
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Failed to read knowledge graph",
                "message": str(exc),
            },
        )