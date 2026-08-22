import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.research import Citation, Dataset, ExperimentPlan, LiteraturePaper, ResearchGap, RoadmapEntry, SupervisorReview, ToolRecommendation
    from app.models.user import User


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"
    archived = "archived"


class ResearchProject(UUIDTimestampMixin, Base):
    __tablename__ = "research_projects"
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    research_idea: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.draft, nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    owner: Mapped["User"] = relationship(back_populates="projects")
    papers: Mapped[list["LiteraturePaper"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    datasets: Mapped[list["Dataset"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    tools: Mapped[list["ToolRecommendation"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    gaps: Mapped[list["ResearchGap"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    experiments: Mapped[list["ExperimentPlan"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    citations: Mapped[list["Citation"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    roadmap_entries: Mapped[list["RoadmapEntry"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    reviews: Mapped[list["SupervisorReview"]] = relationship(back_populates="project", cascade="all, delete-orphan")
