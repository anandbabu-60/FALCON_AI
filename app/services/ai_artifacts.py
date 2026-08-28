import uuid
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai import AIArtifact
from app.repositories.base import BaseRepository
from app.services.projects import get_owned_project


def save_artifact(db: Session, project_id: uuid.UUID | None, user_id: uuid.UUID, artifact_type: str, input_text: str | None, output_payload: Any, model_name: str | None = None) -> AIArtifact | None:
    if project_id is None:
        return None
    get_owned_project(db, project_id, user_id)
    output_payload = jsonable_encoder(output_payload)
    return BaseRepository(AIArtifact).create(db, {"project_id": project_id, "user_id": user_id, "artifact_type": artifact_type, "input_text": input_text, "output_payload": output_payload, "model_name": model_name})


def list_artifacts(db: Session, project_id: uuid.UUID, user_id: uuid.UUID, page: int, size: int):
    get_owned_project(db, project_id, user_id)
    statement = select(AIArtifact).where(AIArtifact.project_id == project_id).order_by(AIArtifact.created_at.desc())
    return BaseRepository(AIArtifact).list(db, statement, page, size)
