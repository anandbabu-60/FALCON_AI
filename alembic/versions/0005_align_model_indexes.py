"""align indexes and remove the legacy user verification column

Revision ID: 0005_align_model_indexes
Revises: 0004_password_reset_tokens
"""

from alembic import op


revision = "0005_align_model_indexes"
down_revision = "0004_password_reset_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Older deployments briefly had this column before registration OTPs were
    # moved to pending_registrations. IF EXISTS keeps the migration safe for
    # fresh Render databases created from the current 0001 revision.
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS email_verified")

    # SQLAlchemy's unique=True, index=True is represented as a unique index.
    # The original migrations created a separate unique constraint and index.
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key")
    op.execute("DROP INDEX IF EXISTS ix_users_email")
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.execute("ALTER TABLE pending_registrations DROP CONSTRAINT IF EXISTS pending_registrations_email_key")
    op.execute("DROP INDEX IF EXISTS ix_pending_registrations_email")
    op.create_index("ix_pending_registrations_email", "pending_registrations", ["email"], unique=True)

    op.create_index("ix_literature_papers_title", "literature_papers", ["title"])
    op.create_index("ix_literature_papers_doi", "literature_papers", ["doi"])
    op.create_index("ix_datasets_name", "datasets", ["name"])
    op.create_index("ix_datasets_domain", "datasets", ["domain"])
    op.create_index("ix_tool_recommendations_name", "tool_recommendations", ["name"])
    op.create_index("ix_tool_recommendations_category", "tool_recommendations", ["category"])
    op.create_index("ix_citations_paper_id", "citations", ["paper_id"])


def downgrade() -> None:
    op.drop_index("ix_citations_paper_id", table_name="citations")
    op.drop_index("ix_tool_recommendations_category", table_name="tool_recommendations")
    op.drop_index("ix_tool_recommendations_name", table_name="tool_recommendations")
    op.drop_index("ix_datasets_domain", table_name="datasets")
    op.drop_index("ix_datasets_name", table_name="datasets")
    op.drop_index("ix_literature_papers_doi", table_name="literature_papers")
    op.drop_index("ix_literature_papers_title", table_name="literature_papers")

    op.drop_index("ix_pending_registrations_email", table_name="pending_registrations")
    op.create_unique_constraint("pending_registrations_email_key", "pending_registrations", ["email"])
    op.create_index("ix_pending_registrations_email", "pending_registrations", ["email"])

    op.drop_index("ix_users_email", table_name="users")
    op.create_unique_constraint("users_email_key", "users", ["email"])
    op.create_index("ix_users_email", "users", ["email"])
