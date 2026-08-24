"""Add updated_at to service_order_status_history

Revision ID: 002
Revises: 001
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "service_order_status_history",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("service_order_status_history", "updated_at")
