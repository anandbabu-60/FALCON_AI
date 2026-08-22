from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


from app.analyzer import analyze_research_idea
from app.literature import search_literature
from app.paper_analyzer import analyze_paper


from app.theme_analyzer import analyze_research_themes
from app.gap_analyzer import analyze_research_gaps


app = FastAPI(
    title="ResearchPilot AI",
    description="AI Research & Project Collaboration Agent",
    version="0.1.0"
)


class ResearchIdea(BaseModel):
    title: str
    research_idea: str
class LiteratureSearch(BaseModel):
    query: str
    limit: int = 10
class PaperInput(BaseModel):
    title: str
    abstract: str
class ThemeAnalysisRequest(BaseModel):
    papers: List[str]
class GapAnalysisRequest(BaseModel):
    research_topic: str
    paper_analyses: List[str]
    theme_analysis: str

@app.get("/")
def root():
    return {
        "message": "ResearchPilot AI is running!"
    }


@app.post("/research-project")
def create_research_project(project: ResearchIdea):

    return {
        "message": "Research project created successfully",
        "project": {
            "title": project.title,
            "research_idea": project.research_idea,
            "status": "created"
        }
    }


@app.post("/analyze-research")
def analyze_research(project: ResearchIdea):

    analysis = analyze_research_idea(
        project.research_idea
    )

    return {
        "message": "Research idea analyzed successfully",
        "analysis": analysis.model_dump()
    }
@app.post("/literature/search")
async def literature_search(search: LiteratureSearch):

    papers = await search_literature(
        search.query,
        search.limit
    )

    return {
        "message": "Literature retrieved successfully",
        "query": search.query,
        "count": len(papers),
        "papers": papers
    }
@app.post("/papers/analyze")
def paper_analysis(paper: PaperInput):

    analysis = analyze_paper(
        paper.title,
        paper.abstract
    )

    return {
        "message": "Paper analyzed successfully",
        "paper": {
            "title": paper.title
        },
        "analysis": analysis.model_dump()
    }
@app.post("/research/themes")
def research_theme_analysis(request: ThemeAnalysisRequest):

    analysis = analyze_research_themes(
        request.papers
    )

    return {
        "message": "Research themes analyzed successfully",
        "analysis": analysis.model_dump()
    }
@app.post("/research/gaps")
def research_gap_analysis(request: GapAnalysisRequest):

    analysis = analyze_research_gaps(
        request.research_topic,
        request.paper_analyses,
        request.theme_analysis
    )

    return {
        "message": "Research gap analysis completed",
        "analysis": analysis.model_dump()
    }