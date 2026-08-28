import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.project import ResearchProject
    from app.models.user import User


class AIArtifact(UUIDTimestampMixin, Base):
    __tablename__ = "ai_artifacts"

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_projects.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    input_text: Mapped[str | None] = mapped_column(Text)
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(120))

    project: Mapped["ResearchProject"] = relationship(back_populates="ai_artifacts")
    user: Mapped["User"] = relationship()
