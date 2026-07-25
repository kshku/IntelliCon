"""add users table for RBAC

Revision ID: 002_add_users
Revises: 001_initial
Create Date: 2025-07-25
"""

from collections.abc import Sequence

import sqlalchemy as sa
from passlib.context import CryptContext

from alembic import op

revision: str = "002_add_users"
down_revision: str = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("employee_id", sa.Integer(), unique=True, nullable=False),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_employee_id", "users", ["employee_id"])

    # Seed default users
    users_table = sa.table(
        "users",
        sa.column("employee_id", sa.Integer),
        sa.column("username", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("role", sa.String),
    )
    op.bulk_insert(
        users_table,
        [
            {
                "employee_id": 1,
                "username": "admin",
                "password_hash": pwd_context.hash("admin"),
                "role": "admin",
            },
            {
                "employee_id": 2,
                "username": "investigator",
                "password_hash": pwd_context.hash("inv123"),
                "role": "investigator",
            },
            {
                "employee_id": 3,
                "username": "supervisor",
                "password_hash": pwd_context.hash("sup123"),
                "role": "supervisor",
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_users_employee_id", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
