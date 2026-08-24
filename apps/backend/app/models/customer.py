import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Customer(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    document: Mapped[str | None] = mapped_column(String(30), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    company: Mapped["Company"] = relationship("Company", back_populates="customers")
    devices: Mapped[list["Device"]] = relationship(
        "Device", back_populates="customer", lazy="selectin"
    )
