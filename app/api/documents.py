import uuid

from fastapi import APIRouter, File, Query, UploadFile, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.common import Page
from app.schemas.documents import DocumentResponse, DocumentTextResponse
from app.services.documents import get_document, list_documents, save_upload

router = APIRouter(prefix="/projects/{project_id}/documents", tags=["Documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession, file: UploadFile = File(...)):
    return save_upload(db, project_id, current_user.id, file)


@router.get("", response_model=Page[DocumentResponse])
def get_documents(project_id: uuid.UUID, current_user: CurrentUser, db: DBSession, page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    items, total = list_documents(db, project_id, current_user.id, page, size)
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{document_id}", response_model=DocumentTextResponse)
def get_document_text(project_id: uuid.UUID, document_id: uuid.UUID, current_user: CurrentUser, db: DBSession):
    return get_document(db, project_id, document_id, current_user.id)
