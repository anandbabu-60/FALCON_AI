import uuid
from typing import Any

from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel

from app.api.deps import CurrentUser, DBSession
from app.models.research import Citation, Dataset, ExperimentPlan, LiteraturePaper, ResearchGap, RoadmapEntry, SupervisorReview, ToolRecommendation
from app.repositories.base import BaseRepository
from app.schemas.common import Page
from app.schemas.research import CitationCreate, CitationResponse, CitationUpdate, DatasetCreate, DatasetResponse, DatasetUpdate, ExperimentCreate, ExperimentResponse, ExperimentUpdate, GapCreate, GapResponse, GapUpdate, PaperCreate, PaperResponse, PaperUpdate, ReviewCreate, ReviewResponse, ReviewUpdate, RoadmapCreate, RoadmapResponse, RoadmapUpdate, ToolCreate, ToolResponse, ToolUpdate
from app.services.resources import create_resource, get_resource, list_resources


def resource_router(prefix: str, tag: str, model: type, create_schema: type[BaseModel], update_schema: type[BaseModel], response_schema: type[BaseModel], search_field: str | None = None) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])
    repository = BaseRepository(model)

    @router.post("", response_model=response_schema, status_code=status.HTTP_201_CREATED)
    def create(project_id: uuid.UUID, payload: create_schema, current_user: CurrentUser, db: DBSession):
        return create_resource(db, model, project_id, current_user.id, payload.model_dump())

    @router.get("", response_model=Page[response_schema])
    def list_all(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100), search: str | None = None):
        items, total = list_resources(db, model, project_id, current_user.id, page, size, search, search_field)
        return {"items": items, "total": total, "page": page, "size": size}

    @router.get("/{resource_id}", response_model=response_schema)
    def get_one(project_id: uuid.UUID, resource_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
        return get_resource(db, model, project_id, resource_id, current_user.id)

    @router.patch("/{resource_id}", response_model=response_schema)
    def update(project_id: uuid.UUID, resource_id: uuid.UUID, payload: update_schema, current_user: CurrentUser, db: DBSession):
        item = get_resource(db, model, project_id, resource_id, current_user.id)
        return repository.update(db, item, payload.model_dump(exclude_unset=True))

    @router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete(project_id: uuid.UUID, resource_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
        repository.delete(db, get_resource(db, model, project_id, resource_id, current_user.id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router


routers = [
    resource_router("/projects/{project_id}/papers", "Literature", LiteraturePaper, PaperCreate, PaperUpdate, PaperResponse, "title"),
    resource_router("/projects/{project_id}/datasets", "Datasets", Dataset, DatasetCreate, DatasetUpdate, DatasetResponse, "name"),
    resource_router("/projects/{project_id}/tools", "Tool Recommendations", ToolRecommendation, ToolCreate, ToolUpdate, ToolResponse, "name"),
    resource_router("/projects/{project_id}/gaps", "Research Gaps", ResearchGap, GapCreate, GapUpdate, GapResponse, "problem"),
    resource_router("/projects/{project_id}/experiments", "Experiment Plans", ExperimentPlan, ExperimentCreate, ExperimentUpdate, ExperimentResponse, "methodology"),
    resource_router("/projects/{project_id}/citations", "Citations", Citation, CitationCreate, CitationUpdate, CitationResponse),
    resource_router("/projects/{project_id}/roadmap", "Roadmap", RoadmapEntry, RoadmapCreate, RoadmapUpdate, RoadmapResponse, "task"),
    resource_router("/projects/{project_id}/reviews", "Supervisor Reviews", SupervisorReview, ReviewCreate, ReviewUpdate, ReviewResponse, "supervisor_name"),
]
