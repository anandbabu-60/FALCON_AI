import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import DocumentStatus, ResearchDocument
from app.models.project import ResearchProject
from app.services.projects import get_owned_project

ALLOWED_TYPES = {"application/pdf", "text/plain"}
ALLOWED_SUFFIXES = {".pdf", ".txt"}


def _extract_text(path: Path, content_type: str) -> tuple[str, int]:
    if content_type == "text/plain" or path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="replace"), 1
    import fitz

    with fitz.open(path) as pdf:
        pages = [page.get_text().strip() for page in pdf]
    return "\n\n".join(text for text in pages if text), len(pages)


def _index_pdf(path: Path, source_name: str, project_id: uuid.UUID) -> tuple[bool, int, str | None]:
    settings = get_settings()
    if not settings.enable_document_indexing or path.suffix.lower() != ".pdf":
        return False, 0, None
    try:
        from app.rag.ingest import ingest_pdf

        chunks = ingest_pdf(str(path), source_name=source_name, project_id=str(project_id))
        return True, len(chunks), None
    except Exception as exc:  # indexing is optional; extraction should still succeed
        return False, 0, str(exc)


def save_upload(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, upload: UploadFile) -> ResearchDocument:
    project = get_owned_project(db, project_id, user_id)
    suffix = Path(upload.filename or "").suffix.lower()
    content_type = upload.content_type or "application/octet-stream"
    if content_type not in ALLOWED_TYPES and suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDF and TXT documents are supported")
    content = upload.file.read()
    max_bytes = get_settings().max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"Document exceeds {get_settings().max_upload_size_mb} MB limit")

    root = Path(get_settings().storage_dir) / "documents" / str(user_id) / str(project.id)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{uuid.uuid4().hex}{suffix or '.bin'}"
    path.write_bytes(content)
    document = ResearchDocument(project_id=project.id, file_name=upload.filename or path.name, content_type=content_type, storage_path=str(path), status=DocumentStatus.processing)
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        text, page_count = _extract_text(path, content_type)
        indexed, chunks, index_error = _index_pdf(path, document.file_name, project.id)
        document.extracted_text = text
        document.page_count = page_count
        document.chunk_count = chunks
        document.indexed = indexed
        document.status = DocumentStatus.ready
        document.error_message = index_error
    except Exception as exc:
        document.status = DocumentStatus.failed
        document.error_message = str(exc)
    db.commit()
    db.refresh(document)
    return document


def list_documents(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, page: int, size: int):
    from app.repositories.base import BaseRepository

    get_owned_project(db, project_id, user_id)
    statement = select(ResearchDocument).where(ResearchDocument.project_id == project_id).order_by(ResearchDocument.created_at.desc())
    return BaseRepository(ResearchDocument).list(db, statement, page, size)


def get_document(db: Session, project_id: uuid.UUID, document_id: uuid.UUID, user_id: uuid.UUID) -> ResearchDocument:
    get_owned_project(db, project_id, user_id)
    document = db.scalar(select(ResearchDocument).where(ResearchDocument.id == document_id, ResearchDocument.project_id == project_id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document
