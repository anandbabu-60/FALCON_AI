from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from app.rag.rag_pipeline import answer_question
from app.services.paper_analyzer import analyze_paper
from app.services.theme_analyzer import analyze_research_themes
from app.services.gap_analyzer import analyze_research_gaps
from app.agents.research_manager import ResearchManager


router = APIRouter(
    prefix="/ai",
    tags=["AI Service"]
)


# ============================================================
# REQUEST MODELS
# ============================================================

class AIQuestionRequest(BaseModel):
    query: str
    top_k: int = 5
    source: str | None = None


class AIPaperRequest(BaseModel):
    title: str
    abstract: str


class AIThemeRequest(BaseModel):
    papers: List[str]


class AIGapRequest(BaseModel):
    research_topic: str
    paper_analyses: List[str]
    theme_analysis: str


class AIWorkflowRequest(BaseModel):
    research_topic: str
    papers: List[dict] = []


# ============================================================
# RAG QUESTION ANSWERING
# ============================================================

@router.post("/ask")
def ai_ask(request: AIQuestionRequest):

    return answer_question(
        query=request.query,
        top_k=request.top_k,
        source=request.source
    )


# ============================================================
# PAPER ANALYSIS
# ============================================================

@router.post("/analyze-paper")
def ai_analyze_paper(request: AIPaperRequest):

    result = analyze_paper(
        title=request.title,
        abstract=request.abstract
    )

    return {
        "success": True,
        "result": result.model_dump()
    }


# ============================================================
# THEME ANALYSIS
# ============================================================

@router.post("/analyze-themes")
def ai_analyze_themes(request: AIThemeRequest):

    result = analyze_research_themes(
        request.papers
    )

    return {
        "success": True,
        "result": result.model_dump()
    }


# ============================================================
# RESEARCH GAP ANALYSIS
# ============================================================

@router.post("/analyze-gaps")
def ai_analyze_gaps(request: AIGapRequest):

    result = analyze_research_gaps(
        research_topic=request.research_topic,
        paper_analyses=request.paper_analyses,
        theme_analysis=request.theme_analysis
    )

    return {
        "success": True,
        "result": result.model_dump()
    }


# ============================================================
# MULTI-AGENT WORKFLOW
# ============================================================

@router.post("/workflow")
def ai_workflow(request: AIWorkflowRequest):

    manager = ResearchManager()

    result = manager.run_research_workflow(
        research_topic=request.research_topic,
        papers=request.papers
    )

    return {
        "success": True,
        "research_topic": request.research_topic,
        "result": result
    }