import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ServiceOrderStatusHistory(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "service_order_status_history"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    service_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service_orders.id"), nullable=False
    )
    previous_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    service_order: Mapped["ServiceOrder"] = relationship(
        "ServiceOrder", back_populates="status_history"
    )
