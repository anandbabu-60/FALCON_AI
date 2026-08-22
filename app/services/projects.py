import uuid

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.project import ResearchProject
from app.repositories.base import BaseRepository

projects = BaseRepository(ResearchProject)


def get_owned_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> ResearchProject:
    project = db.scalar(select(ResearchProject).where(ResearchProject.id == project_id, ResearchProject.owner_id == user_id))
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def list_owned_projects(db: Session, user_id: uuid.UUID, page: int, size: int, search: str | None, domain: str | None, project_status: str | None):
    stmt = select(ResearchProject).where(ResearchProject.owner_id == user_id).order_by(ResearchProject.updated_at.desc())
    if search:
        term = f"%{search}%"; stmt = stmt.where(or_(ResearchProject.title.ilike(term), ResearchProject.research_idea.ilike(term)))
    if domain: stmt = stmt.where(ResearchProject.domain.ilike(f"%{domain}%"))
    if project_status: stmt = stmt.where(ResearchProject.status == project_status)
    return projects.list(db, stmt, page, size)
