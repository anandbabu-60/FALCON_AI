import uuid
import re
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.core.config import get_settings
from app.models.research import Citation, Dataset, ExperimentPlan, LiteraturePaper, ResearchGap, ToolRecommendation
from app.services.ai_artifacts import save_artifact
from app.services.projects import get_owned_project
from app.services.workflow_materializer import materialize_workflow
from app.services.literature_search import save_search_results, search_scholarly_works

router = APIRouter(prefix="/ai", tags=["AI Service"])


@router.get("/health")
def ai_health():
    from app.integrations.gemini import health_status
    return health_status()


class AIQuestionRequest(BaseModel):
    query: str = Field(min_length=2, max_length=10000)
    top_k: int = Field(default=5, ge=1, le=20)
    source: str | None = None
    project_id: uuid.UUID | None = None


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    project_id: uuid.UUID | None = None


class AIResearchSourcesRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=2000)
    project_id: uuid.UUID | None = None
    limit: int = Field(default=10, ge=1, le=25)
    save_results: bool = False


class AIPaperRequest(BaseModel):
    title: str = Field(min_length=2, max_length=1000)
    abstract: str = Field(min_length=2, max_length=30000)
    project_id: uuid.UUID | None = None


class AIThemeRequest(BaseModel):
    papers: list[str] = Field(min_length=1, max_length=50)
    project_id: uuid.UUID | None = None


class AIGapRequest(BaseModel):
    research_topic: str = Field(min_length=2, max_length=2000)
    paper_analyses: list[str] = Field(default_factory=list, max_length=50)
    theme_analysis: str = "Not specified"
    project_id: uuid.UUID | None = None


class AIWorkflowRequest(BaseModel):
    research_topic: str = Field(min_length=2, max_length=2000)
    papers: list[dict[str, Any]] = Field(default_factory=list, max_length=50)
    project_id: uuid.UUID | None = None
    persist_resources: bool = True


class AIProjectActionRequest(BaseModel):
    project_id: uuid.UUID


def _scope(project_id: uuid.UUID | None, user: CurrentUser, db: DBSession) -> None:
    if project_id:
        get_owned_project(db, project_id, user.id)


def _is_greeting(message: str) -> bool:
    normalized = re.sub(r"[^a-z ]+", " ", message.lower()).strip()
    return normalized in {
        "hi", "hii", "hello", "hey", "good morning", "good afternoon",
        "good evening", "hi there", "hello there", "hey there", "how are you",
        "what can you do",
    }


def _is_casual_message(message: str) -> bool:
    normalized = re.sub(r"[^a-z ]+", " ", message.lower()).strip()
    return normalized in {
        "ok", "okay", "okk", "ok dude", "thanks", "thank you", "got it",
        "great", "nice", "cool", "sure", "yes", "yep", "no", "bye", "goodbye",
    }


def _greeting_answer(project: Any | None) -> str:
    if project:
        return (
            f"Hello! I'm your research copilot for **{project.title}**. "
            "I can help you find relevant papers, identify evidence gaps, "
            "recommend datasets, plan experiments, and build your roadmap. "
            "What would you like to work on first?"
        )
    return (
        "Hello! I'm your research copilot. I can help you find relevant papers, "
        "identify research gaps, recommend datasets, plan experiments, and build "
        "an M.Tech roadmap. Create or select a project to get started."
    )


def _project_context_resources(project: Any, db: DBSession) -> tuple[list[str], str]:
    gaps = [gap.research_gap for gap in db.scalars(select(ResearchGap).where(ResearchGap.project_id == project.id).limit(10)).all()]
    experiment = db.scalars(select(ExperimentPlan).where(ExperimentPlan.project_id == project.id).order_by(ExperimentPlan.created_at.desc()).limit(1)).first()
    methodology = experiment.methodology if experiment else "Not specified"
    return gaps, methodology


def _fallback_datasets(topic: str) -> list[dict[str, Any]]:
    text = topic.lower()
    if any(word in text for word in ("plant", "crop", "disease", "leaf")):
        return [
            {"name": "PlantVillage", "purpose": "Labeled leaf images for plant disease classification.", "relevance": "A reproducible baseline for image-based plant disease detection.", "source": "PlantVillage project", "download_link": "https://github.com/spMohanty/PlantVillage-Dataset", "license": "CC BY-SA 3.0", "size": "54,306 images", "domain": "Agriculture / Computer Vision"},
            {"name": "PlantDoc", "purpose": "Real-world plant disease images collected in varied environments.", "relevance": "Useful for evaluating field-domain robustness beyond laboratory images.", "source": "PlantDoc dataset", "download_link": "https://github.com/pratikkayal/PlantDoc-Dataset", "license": "Research use; verify terms", "size": "2,598 images", "domain": "Agriculture / Computer Vision"},
        ]
    if any(word in text for word in ("intrusion", "cyber", "network", "iot", "attack")):
        return [
            {"name": "UNSW-NB15", "purpose": "Network traffic records with normal and attack classes.", "relevance": "A widely used benchmark for intrusion-detection baselines.", "source": "UNSW Canberra Cyber", "download_link": "https://research.unsw.edu.au/projects/unsw-nb15-dataset", "license": "Research use; verify terms", "size": "2.5 million records", "domain": "Cybersecurity / IoT"},
            {"name": "CICIDS2017", "purpose": "Labeled benign and attack network flows across multiple attack types.", "relevance": "Supports reproducible comparison of intrusion-detection methods.", "source": "Canadian Institute for Cybersecurity", "download_link": "https://www.unb.ca/cic/datasets/ids-2017.html", "license": "Research use; verify terms", "size": "PCAP and flow files", "domain": "Cybersecurity"},
        ]
    return [{"name": "UCI Machine Learning Repository", "purpose": "Curated datasets for reproducible machine-learning experiments.", "relevance": "Provides a documented starting point while a domain-specific dataset is selected.", "source": "University of California, Irvine", "download_link": "https://archive.ics.uci.edu/", "license": "Varies by dataset", "size": "Varies", "domain": "Machine Learning"}]


def _fallback_tools(topic: str) -> list[dict[str, Any]]:
    text = topic.lower()
    tools = [
        {"name": "Python", "purpose": "Experiment scripting and reproducible analysis.", "relevance": "Core language for data preparation, modeling, and evaluation.", "category": "Programming", "official_website": "https://www.python.org/", "license": "PSF License"},
        {"name": "scikit-learn", "purpose": "Classical machine-learning models and evaluation utilities.", "relevance": "Useful for baseline models and consistent metrics.", "category": "Machine learning", "official_website": "https://scikit-learn.org/", "license": "BSD-3-Clause"},
        {"name": "MLflow", "purpose": "Track experiments, parameters, metrics, and artifacts.", "relevance": "Improves reproducibility when comparing research experiments.", "category": "Experiment tracking", "official_website": "https://mlflow.org/", "license": "Apache-2.0"},
    ]
    if any(word in text for word in ("federated", "privacy", "iot")):
        tools.insert(1, {"name": "Flower", "purpose": "Build and evaluate federated-learning simulations.", "relevance": "Supports client/server FL experiments without sharing raw data.", "category": "Federated learning", "official_website": "https://flower.ai/", "license": "Apache-2.0"})
    if any(word in text for word in ("image", "vision", "plant", "disease")):
        tools.insert(1, {"name": "PyTorch", "purpose": "Deep-learning training and computer-vision experiments.", "relevance": "Supports reproducible CNN and transformer baselines.", "category": "Deep learning", "official_website": "https://pytorch.org/", "license": "BSD-style"})
    return tools


def _citation_strings(paper: LiteraturePaper) -> dict[str, str]:
    authors = paper.authors or "Unknown author"
    year = paper.year or "n.d."
    title = paper.title.rstrip(".")
    publication = paper.publication or ""
    doi = f" https://doi.org/{paper.doi}" if paper.doi else ""
    return {
        "apa": f"{authors} ({year}). {title}. {publication}.{doi}".strip(),
        "ieee": f"{authors}, \"{title},\" {publication}, {year}.{doi}".strip(),
        "bibtex": f"@article{{{str(paper.id)[:8]}, title={{{title}}}, author={{{authors}}}, year={{{year}}}}}",
        "mla": f"{authors}. \"{title}.\" {publication}, {year}.{doi}".strip(),
        "ris": f"TY  - JOUR\nTI  - {title}\nAU  - {authors}\nPY  - {year}\nDO  - {paper.doi or ''}\nER  -",
    }


def _fallback_chat_answer(message: str, project: Any | None, papers: list[LiteraturePaper], gaps: list[str]) -> str:
    """Return a transparent, local response when Gemini is rate-limited.

    This deliberately avoids invented findings: it only reports records that
    are already stored in PostgreSQL and tells the student what to do next.
    """
    normalized = message.strip().lower()
    if normalized in {"hi", "hii", "hello", "hey", "hi there", "hello there"}:
        greeting = "Hello! I'm your research copilot."
        if project:
            return f"{greeting} Your active project is **{project.title}**. I can help you review saved papers, identify gaps, choose datasets, and plan experiments. Ask me about your project whenever you’re ready."
        return f"{greeting} Create or select a research project, then I can connect your papers, gaps, datasets, experiments, and roadmap."
    lines = [
        "I’m currently working in evidence-only mode because the Gemini quota is unavailable.",
        "",
        f"Your question: {message}",
    ]
    if project:
        lines.extend(["", f"**Project context**: {project.title}", f"Research idea: {project.research_idea}", f"Saved papers: {len(papers)}", f"Saved research gaps: {len(gaps)}"])
        if papers:
            lines.extend(["", "**Saved literature available for review**"])
            lines.extend(f"- {paper.title} ({paper.year or 'year unavailable'})" for paper in papers[:5])
        else:
            lines.extend(["", "No project-specific papers are saved yet. Use **Gather papers** to retrieve scholarly sources."])
        if not gaps:
            lines.extend(["", "No saved research-gap analysis is available yet. Run the roadmap/workflow after Gemini quota is restored."])
    else:
        lines.extend(["", "Select a project to receive evidence-grounded answers from its saved records."])
    lines.extend(["", "I have not inferred research claims or statistics without a verified source. Retry AI enrichment after the quota resets."])
    return "\n".join(lines)


@router.post("/ask")
def ai_ask(request: AIQuestionRequest, current_user: CurrentUser, db: DBSession):
    from app.rag.rag_pipeline import answer_question

    _scope(request.project_id, current_user, db)
    return answer_question(query=request.query, top_k=request.top_k, source=request.source, project_id=str(request.project_id) if request.project_id else None)


@router.post("/chat")
def ai_chat(request: AIChatRequest, current_user: CurrentUser, db: DBSession):
    from app.integrations.gemini import generate_answer

    _scope(request.project_id, current_user, db)
    if _is_greeting(request.message):
        project = get_owned_project(db, request.project_id, current_user.id) if request.project_id else None
        answer = _greeting_answer(project)
        artifact = save_artifact(db, request.project_id, current_user.id, "chat", request.message, {"answer": answer, "ai_status": "greeting"}, "local-greeting")
        return {
            "answer": answer,
            "sources": [],
            "evidence": [],
            "related_papers": [],
            "research_gaps": [],
            "suggestions": ["Find relevant papers for my project.", "What research gap should I investigate?", "Build my research roadmap."],
            "ai_status": "greeting",
            "project_id": request.project_id,
            "artifact_id": artifact.id if artifact else None,
        }
    if _is_casual_message(request.message):
        project = get_owned_project(db, request.project_id, current_user.id) if request.project_id else None
        answer = (
            f"Got it! I'm here whenever you need help with **{project.title}**. "
            "Ask me to find papers, recommend a dataset or tool, generate citations, "
            "analyze a gap, or update your roadmap."
            if project else
            "Got it! I'm here whenever you're ready. Ask me to find papers, recommend "
            "datasets or tools, generate citations, or build your M.Tech roadmap."
        )
        artifact = save_artifact(db, request.project_id, current_user.id, "chat", request.message, {"answer": answer, "ai_status": "conversation"}, "local-conversation")
        return {
            "answer": answer,
            "sources": [], "evidence": [], "related_papers": [], "research_gaps": [],
            "suggestions": ["Find relevant papers for my project.", "Suggest a dataset and research tool.", "Generate citations for my saved papers."],
            "ai_status": "conversation", "project_id": request.project_id,
            "artifact_id": artifact.id if artifact else None,
        }
    prompt = request.message
    related_papers: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    research_gaps: list[str] = []
    if request.project_id:
        project = get_owned_project(db, request.project_id, current_user.id)
        papers = db.scalars(
            select(LiteraturePaper)
            .where(LiteraturePaper.project_id == request.project_id)
            .order_by(LiteraturePaper.created_at.desc())
            .limit(8)
        ).all()
        research_gaps = [
            gap.research_gap
            for gap in db.scalars(
                select(ResearchGap)
                .where(ResearchGap.project_id == request.project_id)
                .order_by(ResearchGap.created_at.desc())
                .limit(8)
            ).all()
        ]
        paper_context = "\n".join(
            f"- {paper.title} ({paper.year or 'year unavailable'}): {(paper.abstract or '')[:500]}"
            for paper in papers
        ) or "No papers have been saved yet."
        related_papers = [
            {
                "id": str(paper.id),
                "title": paper.title,
                "year": paper.year,
                "doi": paper.doi,
                "url": paper.url,
                "abstract": (paper.abstract or paper.summary or "")[:800],
            }
            for paper in papers
        ]
        evidence = [
            {
                "id": str(index + 1),
                "title": paper.title,
                "year": paper.year,
                "url": paper.url,
                "doi": paper.doi,
                "snippet": (paper.abstract or paper.summary or "")[:500],
            }
            for index, paper in enumerate(papers)
        ]
        prompt = (
            "You are the research copilot for an M.Tech student. Give practical, evidence-aware "
            "answers, clearly separate known evidence from suggestions, and include concrete next "
            "steps. Never invent paper findings, citations, benchmark numbers, or percentages. "
            "If no saved literature is provided, explicitly say that project-specific evidence is "
            "not available and recommend a scholarly search instead of presenting general claims as "
            "a literature review. Use this project context:\n"
            f"Project: {project.title}\nResearch idea: {project.research_idea}\n"
            f"Domain: {project.domain or 'Not specified'}\nSaved literature:\n{paper_context}\n\n"
            f"Student question: {request.message}"
        )
    ai_status = "live"
    try:
        answer = generate_answer(prompt)
    except HTTPException as exc:
        if exc.status_code not in {429, 502, 503}:
            raise
        answer = _fallback_chat_answer(request.message, locals().get("project"), locals().get("papers", []), research_gaps)
        ai_status = "fallback"
    artifact = save_artifact(db, request.project_id, current_user.id, "chat", request.message, {"answer": answer, "ai_status": ai_status}, get_settings().gemini_model)
    source_links = []
    for paper in related_papers:
        link = paper.get("url") or (f"https://doi.org/{paper['doi']}" if paper.get("doi") else None)
        if link:
            source_links.append(link)
    suggestions = [
        "Which saved paper should I analyze in detail?",
        "Compare the methods and evaluation metrics in the saved papers.",
        "Turn this into a week-by-week experiment plan.",
    ]
    return {
        "answer": answer,
        "sources": source_links,
        "evidence": evidence,
        "related_papers": related_papers,
        "research_gaps": research_gaps,
        "suggestions": suggestions,
        "ai_status": ai_status,
        "project_id": request.project_id,
        "artifact_id": artifact.id if artifact else None,
    }


@router.post("/recommend-datasets")
def ai_recommend_datasets(request: AIProjectActionRequest, current_user: CurrentUser, db: DBSession):
    project = get_owned_project(db, request.project_id, current_user.id)
    gaps, methodology = _project_context_resources(project, db)
    try:
        from app.services.resource_recommender import recommend_datasets
        result = recommend_datasets(project.research_idea, gaps, methodology)
        items = [item.model_dump() for item in result.recommendations]
        provider = get_settings().gemini_model
    except HTTPException as exc:
        if exc.status_code not in {429, 502, 503}:
            raise
        items = _fallback_datasets(project.research_idea)
        provider = "curated-fallback"
    existing = {name.lower() for name in db.scalars(select(Dataset.name).where(Dataset.project_id == project.id)).all()}
    saved = 0
    for item in items:
        if item["name"].lower() in existing:
            continue
        db.add(Dataset(project_id=project.id, name=item["name"], description=item.get("purpose") or item.get("relevance"), source=item.get("source"), download_link=item.get("download_link"), license=item.get("license"), size=item.get("size"), domain=item.get("domain")))
        existing.add(item["name"].lower()); saved += 1
    db.commit()
    save_artifact(db, project.id, current_user.id, "dataset_recommendations", project.research_idea, {"items": items, "saved_count": saved}, provider)
    return {"items": items, "saved_count": saved, "provider": provider}


@router.post("/recommend-tools")
def ai_recommend_tools(request: AIProjectActionRequest, current_user: CurrentUser, db: DBSession):
    project = get_owned_project(db, request.project_id, current_user.id)
    gaps, methodology = _project_context_resources(project, db)
    try:
        from app.services.tool_recommender import recommend_tools
        result = recommend_tools(project.research_idea, gaps, methodology)
        items = [item.model_dump() for item in result.recommendations]
        provider = get_settings().gemini_model
    except HTTPException as exc:
        if exc.status_code not in {429, 502, 503}:
            raise
        items = _fallback_tools(project.research_idea)
        provider = "curated-fallback"
    existing = {name.lower() for name in db.scalars(select(ToolRecommendation.name).where(ToolRecommendation.project_id == project.id)).all()}
    saved = 0
    for item in items:
        if item["name"].lower() in existing:
            continue
        db.add(ToolRecommendation(project_id=project.id, name=item["name"], category=item.get("category"), official_website=item.get("official_website"), description=item.get("purpose") or item.get("relevance"), license=item.get("license")))
        existing.add(item["name"].lower()); saved += 1
    db.commit()
    save_artifact(db, project.id, current_user.id, "tool_recommendations", project.research_idea, {"items": items, "saved_count": saved}, provider)
    return {"items": items, "saved_count": saved, "provider": provider}


@router.post("/generate-citations")
def ai_generate_citations(request: AIProjectActionRequest, current_user: CurrentUser, db: DBSession):
    project = get_owned_project(db, request.project_id, current_user.id)
    papers = db.scalars(select(LiteraturePaper).where(LiteraturePaper.project_id == project.id).order_by(LiteraturePaper.created_at.asc())).all()
    existing = {str(paper_id) for paper_id in db.scalars(select(Citation.paper_id).where(Citation.project_id == project.id, Citation.paper_id.is_not(None)).all())}
    created = []
    for paper in papers:
        if str(paper.id) in existing:
            continue
        citation = Citation(project_id=project.id, paper_id=paper.id, **_citation_strings(paper))
        db.add(citation); created.append(citation)
    db.commit()
    for citation in created:
        db.refresh(citation)
    items = [jsonable_encoder(citation) for citation in created]
    save_artifact(db, project.id, current_user.id, "citation_generation", f"Generate citations for {len(papers)} saved papers", {"created_count": len(items)}, "local-citation-generator")
    return {"items": items, "created_count": len(items), "paper_count": len(papers)}


@router.post("/research-sources")
def ai_research_sources(request: AIResearchSourcesRequest, current_user: CurrentUser, db: DBSession):
    _scope(request.project_id, current_user, db)
    items = search_scholarly_works(request.topic, request.limit)
    saved_count = save_search_results(db, request.project_id, items) if request.project_id and request.save_results else 0
    answer = f"Found {len(items)} scholarly papers for ‘{request.topic}’ using OpenAlex/Crossref." if items else "No scholarly results were returned. Try a broader topic or check the backend network connection."
    artifact = save_artifact(db, request.project_id, current_user.id, "research_sources", request.topic, {"answer": answer, "items": items, "saved_count": saved_count}, "OpenAlex/Crossref")
    return {"answer": answer, "items": items, "saved_count": saved_count, "artifact_id": artifact.id if artifact else None}


@router.post("/analyze-paper")
def ai_analyze_paper(request: AIPaperRequest, current_user: CurrentUser, db: DBSession):
    from app.services.paper_analyzer import analyze_paper

    _scope(request.project_id, current_user, db)
    result = analyze_paper(title=request.title, abstract=request.abstract)
    artifact = save_artifact(db, request.project_id, current_user.id, "paper_analysis", request.title, result, get_settings().gemini_model)
    return {"success": True, "result": jsonable_encoder(result), "artifact_id": artifact.id if artifact else None}


@router.post("/analyze-themes")
def ai_analyze_themes(request: AIThemeRequest, current_user: CurrentUser, db: DBSession):
    from app.services.theme_analyzer import analyze_research_themes

    _scope(request.project_id, current_user, db)
    result = analyze_research_themes(request.papers)
    artifact = save_artifact(db, request.project_id, current_user.id, "theme_analysis", "\n".join(request.papers), result, get_settings().gemini_model)
    return {"success": True, "result": jsonable_encoder(result), "artifact_id": artifact.id if artifact else None}


@router.post("/analyze-gaps")
def ai_analyze_gaps(request: AIGapRequest, current_user: CurrentUser, db: DBSession):
    from app.services.gap_analyzer import analyze_research_gaps

    _scope(request.project_id, current_user, db)
    result = analyze_research_gaps(request.research_topic, request.paper_analyses, request.theme_analysis)
    artifact = save_artifact(db, request.project_id, current_user.id, "gap_analysis", request.research_topic, result, get_settings().gemini_model)
    return {"success": True, "result": jsonable_encoder(result), "artifact_id": artifact.id if artifact else None}


@router.post("/workflow")
def ai_workflow(request: AIWorkflowRequest, current_user: CurrentUser, db: DBSession):
    from app.agents.research_manager import ResearchManager

    _scope(request.project_id, current_user, db)
    papers = request.papers
    if request.project_id and not papers:
        saved_papers = db.scalars(
            select(LiteraturePaper).where(LiteraturePaper.project_id == request.project_id).order_by(LiteraturePaper.created_at.desc()).limit(50)
        ).all()
        papers = [
            {
                "title": paper.title,
                "abstract": paper.abstract or paper.summary or "No abstract was saved for this paper.",
            }
            for paper in saved_papers
        ]
    result = ResearchManager().run_research_workflow(research_topic=request.research_topic, papers=papers, project_id=str(request.project_id) if request.project_id else None)
    artifact = save_artifact(db, request.project_id, current_user.id, "research_workflow", request.research_topic, result, get_settings().gemini_model)
    persisted = materialize_workflow(db, request.project_id, result) if request.project_id and request.persist_resources else {}
    return {"success": True, "research_topic": request.research_topic, "result": jsonable_encoder(result), "artifact_id": artifact.id if artifact else None, "persisted": persisted}
