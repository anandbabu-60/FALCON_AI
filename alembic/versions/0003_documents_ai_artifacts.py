"""add research documents and persisted AI artifacts

Revision ID: 0003_documents_ai_artifacts
Revises: 0002_pending_registrations
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_documents_ai_artifacts"
down_revision = "0002_pending_registrations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "research_documents",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(120), nullable=False),
        sa.Column("storage_path", sa.String(2048), nullable=False),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("indexed", sa.Boolean(), nullable=False),
        sa.Column("status", sa.Enum("uploaded", "processing", "ready", "failed", name="documentstatus"), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_research_documents_project_id", "research_documents", ["project_id"])
    op.create_table(
        "ai_artifacts",
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_type", sa.String(80), nullable=False),
        sa.Column("input_text", sa.Text()),
        sa.Column("output_payload", sa.JSON(), nullable=False),
        sa.Column("model_name", sa.String(120)),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_artifacts_project_id", "ai_artifacts", ["project_id"])
    op.create_index("ix_ai_artifacts_user_id", "ai_artifacts", ["user_id"])
    op.create_index("ix_ai_artifacts_artifact_type", "ai_artifacts", ["artifact_type"])


def downgrade() -> None:
    op.drop_index("ix_ai_artifacts_artifact_type", table_name="ai_artifacts")
    op.drop_index("ix_ai_artifacts_user_id", table_name="ai_artifacts")
    op.drop_index("ix_ai_artifacts_project_id", table_name="ai_artifacts")
    op.drop_table("ai_artifacts")
    op.drop_index("ix_research_documents_project_id", table_name="research_documents")
    op.drop_table("research_documents")
