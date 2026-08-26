from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.research_manager import ResearchManager

from app.database.connection import SessionLocal
from app.database.crud import (
    create_research_project,
    get_research_project,
    save_paper_to_project,
)

from app.literature import search_literature

from app.rag.ingest import ingest_pdf
from app.rag.rag_pipeline import answer_question

from app.api.ai import router as ai_router
from app.api.knowledge_graph import (
    router as knowledge_graph_router,
)

from app.services.paper_analyzer import analyze_paper
from app.services.theme_analyzer import analyze_research_themes
from app.services.gap_analyzer import analyze_research_gaps


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="ResearchPilot AI",
    description="AI Research & Project Collaboration Agent",
    version="0.7.0",
)


# ============================================================
# AI ROUTER
# ============================================================

app.include_router(ai_router)


# ============================================================
# KNOWLEDGE GRAPH / NEO4J ROUTER
# ============================================================

app.include_router(
    knowledge_graph_router
)


# ============================================================
# CORS Configuration
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Request Models
# ============================================================

class ResearchIdea(BaseModel):
    title: str
    research_idea: str


class PaperInput(BaseModel):
    title: str
    abstract: str


class ThemeAnalysisRequest(BaseModel):
    papers: List[str]


class GapAnalysisRequest(BaseModel):
    research_topic: str
    paper_analyses: List[str]
    theme_analysis: str


class ResearchQuestionRequest(BaseModel):
    query: str
    top_k: int = 5
    source: str | None = None


class FullWorkflowRequest(BaseModel):
    research_topic: str

    # Optional manually supplied papers.
    # If empty, OpenAlex will be searched automatically.
    papers: List[PaperInput] = []

    # Number of papers to retrieve from OpenAlex.
    literature_limit: int = 5

    # Optional research project.
    # If supplied, retrieved papers are saved to SQLite.
    project_id: int | None = None


# ============================================================
# Basic Health Check
# ============================================================

@app.get("/")
def root():

    return {
        "message": "ResearchPilot AI is running!",
        "status": "healthy",
    }


# ============================================================
# Research Project
# ============================================================

@app.post("/research-project")
def create_research_project_endpoint(
    project: ResearchIdea,
):

    db = SessionLocal()

    try:

        created_project = create_research_project(
            db=db,
            title=project.title,
            description=project.research_idea,
        )

        return {
            "message": "Research project created successfully",
            "project": {
                "id": created_project.id,
                "title": created_project.title,
                "research_idea": created_project.description,
                "status": "created",
            },
        }

    finally:

        db.close()


# ============================================================
# Literature Search
# ============================================================

@app.get("/literature/search")
async def literature_search(
    query: str,
    limit: int = 10,
):

    papers = await search_literature(
        query=query,
        limit=limit,
    )

    return {
        "message": "Literature search completed successfully",
        "query": query,
        "papers_found": len(papers),
        "papers": papers,
    }


# ============================================================
# Paper Analysis
# ============================================================

@app.post("/papers/analyze")
def paper_analysis(
    paper: PaperInput,
):

    analysis = analyze_paper(
        title=paper.title,
        abstract=paper.abstract,
    )

    return {
        "message": "Paper analyzed successfully",
        "paper": {
            "title": paper.title,
        },
        "analysis": analysis.model_dump(),
    }


# ============================================================
# Theme Analysis
# ============================================================

@app.post("/research/themes")
def research_theme_analysis(
    request: ThemeAnalysisRequest,
):

    analysis = analyze_research_themes(
        request.papers,
    )

    return {
        "message": "Research themes analyzed successfully",
        "analysis": analysis.model_dump(),
    }


# ============================================================
# Research Gap Analysis
# ============================================================

@app.post("/research/gaps")
def research_gap_analysis(
    request: GapAnalysisRequest,
):

    analysis = analyze_research_gaps(
        research_topic=request.research_topic,
        paper_analyses=request.paper_analyses,
        theme_analysis=request.theme_analysis,
    )

    return {
        "message": "Research gap analysis completed",
        "analysis": analysis.model_dump(),
    }


# ============================================================
# PDF Document Upload
# ============================================================

@app.post("/research/documents/upload")
async def upload_research_document(
    file: UploadFile = File(...),
):
    """
    Upload a PDF research document and ingest it into
    the RAG knowledge base.
    """

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="A file is required.",
        )

    filename = Path(
        file.filename
    ).name

    # --------------------------------------------------------
    # Validate file type
    # --------------------------------------------------------

    if Path(filename).suffix.lower() != ".pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    temporary_path = None

    try:

        # ----------------------------------------------------
        # Save uploaded PDF temporarily
        # ----------------------------------------------------

        with NamedTemporaryFile(
            delete=False,
            suffix=".pdf",
        ) as temporary_file:

            temporary_path = Path(
                temporary_file.name
            )

            file_content = await file.read()

            temporary_file.write(
                file_content
            )

        # ----------------------------------------------------
        # Ingest PDF
        # ----------------------------------------------------

        chunks = ingest_pdf(
            file_path=str(temporary_path),
            source_name=filename,
        )

        # ----------------------------------------------------
        # Return upload result
        # ----------------------------------------------------

        return {
            "message": "PDF uploaded and indexed successfully",
            "filename": filename,
            "pages_processed": len(
                {
                    chunk["metadata"].get("page")
                    for chunk in chunks
                }
            ),
            "chunks_created": len(chunks),
            "status": "indexed",
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "PDF ingestion failed",
                "message": str(e),
            },
        )

    finally:

        # ----------------------------------------------------
        # Delete temporary file
        # ----------------------------------------------------

        if (
            temporary_path
            and temporary_path.exists()
        ):

            try:

                temporary_path.unlink()

            except OSError:

                pass


# ============================================================
# RAG Research Question Answering
# ============================================================

@app.post("/research/ask")
def research_question(
    request: ResearchQuestionRequest,
):

    result = answer_question(
        query=request.query,
        top_k=request.top_k,
        source=request.source,
    )

    return {
        "message": "Research question answered successfully",
        "query": request.query,
        "source": request.source,
        "answer": result["answer"],
        "citations": result["citations"],
        "citation_validation": result.get(
            "citation_validation"
        ),
    }


# ============================================================
# FULL RESEARCH WORKFLOW
# ============================================================

@app.post("/research/workflow")
async def full_research_workflow(
    request: FullWorkflowRequest,
):
    """
    Run the complete ResearchPilot AI workflow.

    Workflow:

    1. Retrieve literature from OpenAlex or use supplied papers.
    2. Optionally save papers to an existing SQLite project.
    3. Run the multi-agent research workflow.
    4. Return the complete research result.
    """

    manager = ResearchManager()

    # ========================================================
    # 1. Get papers
    # ========================================================

    if request.papers:

        papers = [
            {
                "title": paper.title,
                "abstract": paper.abstract,
            }
            for paper in request.papers
        ]

        literature_source = "user_provided"

    else:

        papers = await search_literature(
            query=request.research_topic,
            limit=request.literature_limit,
        )

        papers = [
            {
                "title": paper.get("title") or "Untitled",
                "abstract": paper.get("abstract") or "",
                "id": paper.get("id"),
                "year": paper.get("year"),
                "doi": paper.get("doi"),
                "authors": paper.get("authors", []),
                "url": paper.get("url"),
            }
            for paper in papers
        ]

        literature_source = "openalex"

    # ========================================================
    # 2. Handle no papers
    # ========================================================

    if not papers:

        return {
            "message": "No relevant papers were found.",
            "research_topic": request.research_topic,
            "project_id": request.project_id,
            "papers_found": 0,
            "papers_saved": 0,
            "source": literature_source,
            "result": None,
        }

    # ========================================================
    # 3. Save papers to SQLite project
    # ========================================================

    papers_saved = 0

    if request.project_id is not None:

        db = SessionLocal()

        try:

            project = get_research_project(
                db=db,
                project_id=request.project_id,
            )

            if not project:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Research project "
                        f"{request.project_id} not found."
                    ),
                )

            for paper in papers:

                save_paper_to_project(
                    db=db,
                    project_id=request.project_id,
                    paper_data=paper,
                )

                papers_saved += 1

        finally:

            db.close()

    # ========================================================
    # 4. Run multi-agent research workflow
    # ========================================================

    result = manager.run_research_workflow(
        research_topic=request.research_topic,
        papers=papers,
    )

    # ========================================================
    # 5. Return complete result
    # ========================================================

    return {
        "message": "Research workflow completed successfully",

        "research_topic":
            request.research_topic,

        "project_id":
            request.project_id,

        "papers_found":
            len(papers),

        "papers_saved":
            papers_saved,

        "source":
            literature_source,

        "result":
            result,
    }