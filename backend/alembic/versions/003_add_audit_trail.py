"""add audit_trail table

Revision ID: 003_add_audit_trail
Revises: 001_initial
Create Date: 2025-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "003_add_audit_trail"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "audit_trail",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("session_id", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("step_type", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("tool_name", sa.String(), nullable=True),
        sa.Column("tool_output", sa.Text(), nullable=True),
        sa.Column("sql_executed", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_audit_trail_session_id",
        "audit_trail",
        ["session_id"],
    )
    op.create_index(
        "ix_audit_trail_created_at",
        "audit_trail",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_trail_created_at", table_name="audit_trail")
    op.drop_index("ix_audit_trail_session_id", table_name="audit_trail")
    op.drop_table("audit_trail")
