import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.research import ProjectResource
from app.repositories.base import BaseRepository
from app.services.projects import get_owned_project


def list_resources(db: Session, model: type[ProjectResource], project_id: uuid.UUID, user_id: uuid.UUID, page: int, size: int, search: str | None, search_field: str | None):
    get_owned_project(db, project_id, user_id)
    stmt = select(model).where(model.project_id == project_id).order_by(model.created_at.desc())
    if search and search_field:
        stmt = stmt.where(getattr(model, search_field).ilike(f"%{search}%"))
    return BaseRepository(model).list(db, stmt, page, size)


def get_resource(db: Session, model: type[ProjectResource], project_id: uuid.UUID, resource_id: uuid.UUID, user_id: uuid.UUID) -> ProjectResource:
    get_owned_project(db, project_id, user_id)
    item = db.scalar(select(model).where(model.id == resource_id, model.project_id == project_id))
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return item


def create_resource(db: Session, model: type[ProjectResource], project_id: uuid.UUID, user_id: uuid.UUID, payload: dict[str, Any]) -> ProjectResource:
    get_owned_project(db, project_id, user_id)
    return BaseRepository(model).create(db, {**payload, "project_id": project_id})
