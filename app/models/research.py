import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.project import ResearchProject


class RoadmapStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    blocked = "blocked"


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    changes_requested = "changes_requested"


class ProjectResource(UUIDTimestampMixin, Base):
    __abstract__ = True
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), index=True, nullable=False)


class LiteraturePaper(ProjectResource):
    __tablename__ = "literature_papers"
    title: Mapped[str] = mapped_column(String(500), index=True, nullable=False)
    authors: Mapped[str | None] = mapped_column(Text)
    abstract: Mapped[str | None] = mapped_column(Text)
    doi: Mapped[str | None] = mapped_column(String(255), index=True)
    publication: Mapped[str | None] = mapped_column(String(255))
    year: Mapped[int | None] = mapped_column(Integer)
    url: Mapped[str | None] = mapped_column(String(2048))
    summary: Mapped[str | None] = mapped_column(Text)
    keywords: Mapped[str | None] = mapped_column(Text)
    project: Mapped["ResearchProject"] = relationship(back_populates="papers")


class Dataset(ProjectResource):
    __tablename__ = "datasets"
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(255))
    download_link: Mapped[str | None] = mapped_column(String(2048))
    license: Mapped[str | None] = mapped_column(String(120))
    size: Mapped[str | None] = mapped_column(String(100))
    domain: Mapped[str | None] = mapped_column(String(120), index=True)
    project: Mapped["ResearchProject"] = relationship(back_populates="datasets")


class ToolRecommendation(ProjectResource):
    __tablename__ = "tool_recommendations"
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), index=True)
    official_website: Mapped[str | None] = mapped_column(String(2048))
    description: Mapped[str | None] = mapped_column(Text)
    license: Mapped[str | None] = mapped_column(String(120))
    project: Mapped["ResearchProject"] = relationship(back_populates="tools")


class ResearchGap(ProjectResource):
    __tablename__ = "research_gaps"
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    existing_solution: Mapped[str | None] = mapped_column(Text)
    limitation: Mapped[str | None] = mapped_column(Text)
    research_gap: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_innovation: Mapped[str | None] = mapped_column(Text)
    project: Mapped["ResearchProject"] = relationship(back_populates="gaps")


class ExperimentPlan(ProjectResource):
    __tablename__ = "experiment_plans"
    methodology: Mapped[str] = mapped_column(Text, nullable=False)
    algorithms: Mapped[str | None] = mapped_column(Text)
    evaluation_metrics: Mapped[str | None] = mapped_column(Text)
    workflow: Mapped[str | None] = mapped_column(Text)
    expected_results: Mapped[str | None] = mapped_column(Text)
    project: Mapped["ResearchProject"] = relationship(back_populates="experiments")


class Citation(ProjectResource):
    __tablename__ = "citations"
    apa: Mapped[str | None] = mapped_column(Text)
    ieee: Mapped[str | None] = mapped_column(Text)
    bibtex: Mapped[str | None] = mapped_column(Text)
    mla: Mapped[str | None] = mapped_column(Text)
    ris: Mapped[str | None] = mapped_column(Text)
    paper_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("literature_papers.id", ondelete="SET NULL"), index=True)
    project: Mapped["ResearchProject"] = relationship(back_populates="citations")


class RoadmapEntry(ProjectResource):
    __tablename__ = "roadmap_entries"
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    task: Mapped[str] = mapped_column(Text, nullable=False)
    deadline: Mapped[date | None] = mapped_column(Date)
    status: Mapped[RoadmapStatus] = mapped_column(Enum(RoadmapStatus), default=RoadmapStatus.pending, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text)
    project: Mapped["ResearchProject"] = relationship(back_populates="roadmap_entries")


class SupervisorReview(ProjectResource):
    __tablename__ = "supervisor_reviews"
    supervisor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    comments: Mapped[str | None] = mapped_column(Text)
    approval_status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.pending, nullable=False)
    meeting_date: Mapped[date | None] = mapped_column(Date)
    suggestions: Mapped[str | None] = mapped_column(Text)
    project: Mapped["ResearchProject"] = relationship(back_populates="reviews")
