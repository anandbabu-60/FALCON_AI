import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AIArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    artifact_type: str
    input_text: str | None
    output_payload: dict[str, Any]
    model_name: str | None
    created_at: datetime
    updated_at: datetime


class AIArtifactListResponse(BaseModel):
    items: list[AIArtifactResponse]
    total: int
    page: int
    size: int
