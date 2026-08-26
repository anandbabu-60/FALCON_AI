from sqlalchemy.orm import Session

from app.database.models import ResearchProject, Paper


# ============================================================
# Research Projects
# ============================================================

def create_research_project(
    db: Session,
    title: str,
    description: str | None = None
) -> ResearchProject:

    project = ResearchProject(
        title=title,
        description=description
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_research_project(
    db: Session,
    project_id: int
) -> ResearchProject | None:

    return (
        db.query(ResearchProject)
        .filter(
            ResearchProject.id == project_id
        )
        .first()
    )


def get_research_projects(
    db: Session
) -> list[ResearchProject]:

    return (
        db.query(ResearchProject)
        .order_by(
            ResearchProject.id.desc()
        )
        .all()
    )


# ============================================================
# Papers
# ============================================================

def create_paper(
    db: Session,
    project_id: int,
    title: str,
    abstract: str | None = None,
    authors: str | None = None
) -> Paper:

    paper = Paper(
        title=title,
        abstract=abstract,
        authors=authors,
        project_id=project_id
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return paper


def get_project_papers(
    db: Session,
    project_id: int
) -> list[Paper]:

    return (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id
        )
        .all()
    )


def save_paper_to_project(
    db: Session,
    project_id: int,
    paper_data: dict
) -> Paper:

    title = paper_data.get("title") or "Untitled"

    # --------------------------------------------------------
    # Avoid duplicate papers in the same project
    # --------------------------------------------------------

    existing = (
        db.query(Paper)
        .filter(
            Paper.project_id == project_id,
            Paper.title == title
        )
        .first()
    )

    if existing:
        return existing

    # --------------------------------------------------------
    # Convert OpenAlex authors list to string
    # --------------------------------------------------------

    authors = paper_data.get("authors")

    if isinstance(authors, list):
        authors = ", ".join(
            author
            for author in authors
            if author
        )

    # --------------------------------------------------------
    # Create paper
    # --------------------------------------------------------

    paper = Paper(
        title=title,
        abstract=paper_data.get("abstract"),
        authors=authors,
        project_id=project_id
    )

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return paper