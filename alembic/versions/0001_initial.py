"""initial research collaboration schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("email", sa.String(255), nullable=False), sa.Column("full_name", sa.String(150), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("institution", sa.String(255)), sa.Column("is_active", sa.Boolean(), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("email"))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("research_projects", sa.Column("title", sa.String(255), nullable=False), sa.Column("research_idea", sa.Text(), nullable=False), sa.Column("domain", sa.String(120), nullable=False), sa.Column("description", sa.Text()), sa.Column("status", sa.Enum("draft", "active", "paused", "completed", "archived", name="projectstatus"), nullable=False), sa.Column("owner_id", sa.Uuid(), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_research_projects_owner_id", "research_projects", ["owner_id"]); op.create_index("ix_research_projects_title", "research_projects", ["title"]); op.create_index("ix_research_projects_domain", "research_projects", ["domain"])
    _resource_tables()


def _resource_tables() -> None:
    def base():
        return [sa.Column("project_id", sa.Uuid(), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["project_id"], ["research_projects.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id")]
    tables = {"literature_papers": [sa.Column("title", sa.String(500), nullable=False), sa.Column("authors", sa.Text()), sa.Column("abstract", sa.Text()), sa.Column("doi", sa.String(255)), sa.Column("publication", sa.String(255)), sa.Column("year", sa.Integer()), sa.Column("url", sa.String(2048)), sa.Column("summary", sa.Text()), sa.Column("keywords", sa.Text())], "datasets": [sa.Column("name", sa.String(255), nullable=False), sa.Column("description", sa.Text()), sa.Column("source", sa.String(255)), sa.Column("download_link", sa.String(2048)), sa.Column("license", sa.String(120)), sa.Column("size", sa.String(100)), sa.Column("domain", sa.String(120))], "tool_recommendations": [sa.Column("name", sa.String(255), nullable=False), sa.Column("category", sa.String(120)), sa.Column("official_website", sa.String(2048)), sa.Column("description", sa.Text()), sa.Column("license", sa.String(120))], "research_gaps": [sa.Column("problem", sa.Text(), nullable=False), sa.Column("existing_solution", sa.Text()), sa.Column("limitation", sa.Text()), sa.Column("research_gap", sa.Text(), nullable=False), sa.Column("proposed_innovation", sa.Text())], "experiment_plans": [sa.Column("methodology", sa.Text(), nullable=False), sa.Column("algorithms", sa.Text()), sa.Column("evaluation_metrics", sa.Text()), sa.Column("workflow", sa.Text()), sa.Column("expected_results", sa.Text())], "citations": [sa.Column("apa", sa.Text()), sa.Column("ieee", sa.Text()), sa.Column("bibtex", sa.Text()), sa.Column("mla", sa.Text()), sa.Column("ris", sa.Text()), sa.Column("paper_id", sa.Uuid())], "roadmap_entries": [sa.Column("week_number", sa.Integer(), nullable=False), sa.Column("task", sa.Text(), nullable=False), sa.Column("deadline", sa.Date()), sa.Column("status", sa.Enum("pending", "in_progress", "completed", "blocked", name="roadmapstatus"), nullable=False), sa.Column("remarks", sa.Text())], "supervisor_reviews": [sa.Column("supervisor_name", sa.String(255), nullable=False), sa.Column("comments", sa.Text()), sa.Column("approval_status", sa.Enum("pending", "approved", "changes_requested", name="approvalstatus"), nullable=False), sa.Column("meeting_date", sa.Date()), sa.Column("suggestions", sa.Text())]}
    for name, columns in tables.items():
        if name == "citations": columns.append(sa.ForeignKeyConstraint(["paper_id"], ["literature_papers.id"], ondelete="SET NULL"))
        op.create_table(name, *columns, *base()); op.create_index(f"ix_{name}_project_id", name, ["project_id"])


def downgrade() -> None:
    for table in ["supervisor_reviews", "roadmap_entries", "citations", "experiment_plans", "research_gaps", "tool_recommendations", "datasets", "literature_papers", "research_projects", "users"]: op.drop_table(table)
