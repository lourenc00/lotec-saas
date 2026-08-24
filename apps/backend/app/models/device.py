import uuid

from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Device(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "devices"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str] = mapped_column(String(150), nullable=False)
    color: Mapped[str | None] = mapped_column(String(80), nullable=True)
    imei: Mapped[str | None] = mapped_column(String(30), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    physical_condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped["Company"] = relationship("Company", back_populates=None)
    customer: Mapped["Customer"] = relationship("Customer", back_populates="devices")
