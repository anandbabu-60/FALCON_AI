from pydantic import BaseModel, Field

from app.models.project import ProjectStatus
from app.schemas.common import TimestampedResponse


class ProjectCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    research_idea: str = Field(min_length=10)
    domain: str = Field(min_length=2, max_length=120)
    description: str | None = None
    status: ProjectStatus = ProjectStatus.draft


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    research_idea: str | None = Field(default=None, min_length=10)
    domain: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    status: ProjectStatus | None = None


class ProjectResponse(TimestampedResponse):
    title: str
    research_idea: str
    domain: str
    description: str | None
    status: ProjectStatus
