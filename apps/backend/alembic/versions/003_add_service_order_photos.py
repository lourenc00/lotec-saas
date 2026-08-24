"""Add service_order_photos table

Revision ID: 003
Revises: 002
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_order_photos",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("service_order_id", UUID(as_uuid=True), sa.ForeignKey("service_orders.id"), nullable=False),
        sa.Column("photo_type", sa.String(50), nullable=True),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.BigInteger, nullable=False),
        sa.Column("checksum", sa.String(128), nullable=True),
        sa.Column("uploaded_by_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_photos_company", "service_order_photos", ["company_id"])
    op.create_index("idx_photos_order", "service_order_photos", ["service_order_id"])


def downgrade() -> None:
    op.drop_index("idx_photos_order")
    op.drop_index("idx_photos_company")
    op.drop_table("service_order_photos")
