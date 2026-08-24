"""Add system_settings table

Revision ID: 004
Revises: 003
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(255), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_system_settings_key", "system_settings", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_system_settings_key")
    op.drop_table("system_settings")
