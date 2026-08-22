import uuid

from fastapi import APIRouter, Query, Response, status

from app.api.deps import CurrentUser, DBSession
from app.models.project import ProjectStatus, ResearchProject
from app.repositories.base import BaseRepository
from app.schemas.common import Page
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.projects import get_owned_project, list_owned_projects

router = APIRouter(prefix="/projects", tags=["Research Projects"])
repository = BaseRepository(ResearchProject)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, current_user: CurrentUser, db: DBSession):
    return repository.create(db, {**payload.model_dump(), "owner_id": current_user.id})


@router.get("", response_model=Page)
def list_projects(current_user: CurrentUser, db: DBSession, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), search: str | None = None, domain: str | None = None, project_status: ProjectStatus | None = None):
    items, total = list_owned_projects(db, current_user.id, page, size, search, domain, project_status)
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession): return get_owned_project(db, project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: uuid.UUID, payload: ProjectUpdate, current_user: CurrentUser, db: DBSession):
    return repository.update(db, get_owned_project(db, project_id, current_user.id), payload.model_dump(exclude_unset=True))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    repository.delete(db, get_owned_project(db, project_id, current_user.id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
