import uuid
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampedResponse(ORMModel):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


ResponseT = TypeVar("ResponseT")


class Page(ORMModel, Generic[ResponseT]):
    items: list[ResponseT]
    total: int
    page: int
    size: int
