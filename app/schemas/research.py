import uuid
from datetime import date

from pydantic import BaseModel, Field, HttpUrl

from app.models.research import ApprovalStatus, RoadmapStatus
from app.schemas.common import TimestampedResponse


class PaperCreate(BaseModel):
    title: str = Field(min_length=2, max_length=500); authors: str | None = None; abstract: str | None = None; doi: str | None = None; publication: str | None = None; year: int | None = Field(default=None, ge=1800, le=2100); url: str | None = None; summary: str | None = None; keywords: str | None = None
class PaperUpdate(PaperCreate): title: str | None = Field(default=None, min_length=2, max_length=500)
class PaperResponse(PaperCreate, TimestampedResponse): pass

class DatasetCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255); description: str | None = None; source: str | None = None; download_link: str | None = None; license: str | None = None; size: str | None = None; domain: str | None = None
class DatasetUpdate(DatasetCreate): name: str | None = Field(default=None, min_length=2, max_length=255)
class DatasetResponse(DatasetCreate, TimestampedResponse): pass

class ToolCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255); category: str | None = None; official_website: str | None = None; description: str | None = None; license: str | None = None
class ToolUpdate(ToolCreate): name: str | None = Field(default=None, min_length=2, max_length=255)
class ToolResponse(ToolCreate, TimestampedResponse): pass

class GapCreate(BaseModel):
    problem: str = Field(min_length=2); existing_solution: str | None = None; limitation: str | None = None; research_gap: str = Field(min_length=2); proposed_innovation: str | None = None
class GapUpdate(GapCreate): problem: str | None = Field(default=None, min_length=2); research_gap: str | None = Field(default=None, min_length=2)
class GapResponse(GapCreate, TimestampedResponse): pass

class ExperimentCreate(BaseModel):
    methodology: str = Field(min_length=2); algorithms: str | None = None; evaluation_metrics: str | None = None; workflow: str | None = None; expected_results: str | None = None
class ExperimentUpdate(ExperimentCreate): methodology: str | None = Field(default=None, min_length=2)
class ExperimentResponse(ExperimentCreate, TimestampedResponse): pass

class CitationCreate(BaseModel):
    apa: str | None = None; ieee: str | None = None; bibtex: str | None = None; mla: str | None = None; ris: str | None = None; paper_id: uuid.UUID | None = None
class CitationUpdate(CitationCreate): pass
class CitationResponse(CitationCreate, TimestampedResponse): pass

class RoadmapCreate(BaseModel):
    week_number: int = Field(ge=1, le=104); task: str = Field(min_length=2); deadline: date | None = None; status: RoadmapStatus = RoadmapStatus.pending; remarks: str | None = None
class RoadmapUpdate(RoadmapCreate): week_number: int | None = Field(default=None, ge=1, le=104); task: str | None = Field(default=None, min_length=2); status: RoadmapStatus | None = None
class RoadmapResponse(RoadmapCreate, TimestampedResponse): pass

class ReviewCreate(BaseModel):
    supervisor_name: str = Field(min_length=2, max_length=255); comments: str | None = None; approval_status: ApprovalStatus = ApprovalStatus.pending; meeting_date: date | None = None; suggestions: str | None = None
class ReviewUpdate(ReviewCreate): supervisor_name: str | None = Field(default=None, min_length=2, max_length=255); approval_status: ApprovalStatus | None = None
class ReviewResponse(ReviewCreate, TimestampedResponse): pass
