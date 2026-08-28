from __future__ import annotations

from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.research import LiteraturePaper


def _abstract_from_inverted_index(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        words.extend((position, word) for position in positions)
    return " ".join(word for _, word in sorted(words)) or None


def _openalex_item(item: dict[str, Any]) -> dict[str, Any]:
    location = item.get("primary_location") or {}
    source = location.get("source") or {}
    authors = [
        (author.get("author") or {}).get("display_name")
        for author in item.get("authorships") or []
        if (author.get("author") or {}).get("display_name")
    ]
    doi = item.get("doi")
    landing_url = location.get("landing_page_url") or (doi if doi else None)
    raw_pdf_url = location.get("pdf_url")
    pdf_url = raw_pdf_url.get("url") if isinstance(raw_pdf_url, dict) else raw_pdf_url
    return {
        "external_id": item.get("id"),
        "title": item.get("title") or "Untitled paper",
        "authors": ", ".join(authors) or None,
        "abstract": _abstract_from_inverted_index(item.get("abstract_inverted_index")),
        "doi": doi,
        "publication": source.get("display_name"),
        "year": item.get("publication_year"),
        "url": landing_url,
        "pdf_url": pdf_url,
        "source": "OpenAlex",
    }


def _crossref_item(item: dict[str, Any]) -> dict[str, Any]:
    authors = [
        " ".join(filter(None, [author.get("given"), author.get("family")]))
        for author in item.get("author") or []
    ]
    doi = item.get("DOI")
    return {
        "external_id": f"https://api.crossref.org/works/{doi}" if doi else None,
        "title": (item.get("title") or ["Untitled paper"])[0],
        "authors": ", ".join(authors) or None,
        "abstract": item.get("abstract"),
        "doi": doi,
        "publication": (item.get("container-title") or [None])[0],
        "year": ((item.get("published-print") or item.get("published-online") or {}).get("date-parts") or [[None]])[0][0],
        "url": item.get("URL") or (f"https://doi.org/{doi}" if doi else None),
        "pdf_url": None,
        "source": "Crossref",
    }


def search_scholarly_works(topic: str, limit: int = 10) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 25))
    headers = {"User-Agent": "ResearchMindAI/1.0 (mailto:research@example.com)"}
    try:
        with httpx.Client(timeout=15, follow_redirects=True, headers=headers) as client:
            response = client.get(
                "https://api.openalex.org/works",
                params={"search": topic, "per-page": limit, "sort": "relevance_score:desc"},
            )
            response.raise_for_status()
            items = [_openalex_item(item) for item in response.json().get("results", [])]
            if items:
                return items
    except (httpx.HTTPError, ValueError):
        try:
            with httpx.Client(timeout=15, follow_redirects=True, headers=headers) as client:
                response = client.get(
                    "https://api.crossref.org/works",
                    params={"query": topic, "rows": limit, "select": "DOI,title,author,container-title,published,URL,abstract"},
                )
                response.raise_for_status()
                return [_crossref_item(item) for item in response.json().get("message", {}).get("items", [])]
        except (httpx.HTTPError, ValueError):
            return []


def save_search_results(db: Session, project_id, results: list[dict[str, Any]]) -> int:
    saved = 0
    created: list[LiteraturePaper] = []
    for result in results:
        duplicate = None
        if result.get("doi"):
            duplicate = db.scalar(select(LiteraturePaper).where(LiteraturePaper.project_id == project_id, LiteraturePaper.doi == result["doi"]))
        if duplicate is None:
            duplicate = db.scalar(select(LiteraturePaper).where(LiteraturePaper.project_id == project_id, LiteraturePaper.title == result["title"]))
        if duplicate:
            continue
        paper = LiteraturePaper(
            project_id=project_id,
            title=result["title"],
            authors=result.get("authors"),
            abstract=result.get("abstract"),
            doi=result.get("doi"),
            publication=result.get("publication"),
            year=result.get("year"),
            url=result.get("url") or result.get("pdf_url"),
            summary=None,
            keywords=None,
        )
        db.add(paper)
        created.append(paper)
        saved += 1
    if saved:
        db.commit()
        try:
            from app.integrations.neo4j import is_configured, upsert_paper
            if is_configured():
                for paper in created:
                    upsert_paper(str(project_id), str(paper.id), paper.title, paper.authors, paper.abstract)
        except Exception:
            pass
    return saved
