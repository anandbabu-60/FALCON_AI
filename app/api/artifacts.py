import uuid

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.schemas.ai import AIArtifactListResponse
from app.services.ai_artifacts import list_artifacts

router = APIRouter(prefix="/projects/{project_id}/ai-artifacts", tags=["AI Artifacts"])


@router.get("", response_model=AIArtifactListResponse)
def get_ai_artifacts(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    items, total = list_artifacts(db, project_id, current_user.id, page, size)
    return {"items": items, "total": total, "page": page, "size": size}
