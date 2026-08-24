import uuid

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Text, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class ServiceOrder(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "service_orders"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    os_number: Mapped[int] = mapped_column(nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False
    )
    responsible_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="RECEIVED")

    entry_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    estimated_delivery_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completion_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivery_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    problem_reported: Mapped[str] = mapped_column(Text, nullable=False)
    service_requested: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    service_performed_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    estimated_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    approved_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    discount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    final_value: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    payment_status: Mapped[str | None] = mapped_column(String(30), nullable=True)

    public_tracking_token_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    status_history: Mapped[list["ServiceOrderStatusHistory"]] = relationship(
        "ServiceOrderStatusHistory",
        back_populates="service_order",
        lazy="selectin",
        order_by="ServiceOrderStatusHistory.created_at",
    )
    services: Mapped[list["ServiceOrderService"]] = relationship(
        "ServiceOrderService",
        back_populates="service_order",
        lazy="selectin",
    )
    parts: Mapped[list["ServiceOrderPart"]] = relationship(
        "ServiceOrderPart",
        back_populates="service_order",
        lazy="selectin",
    )
    photos: Mapped[list["ServiceOrderPhoto"]] = relationship(
        "ServiceOrderPhoto",
        back_populates="service_order",
        lazy="selectin",
    )


class ServiceOrderPhoto(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "service_order_photos"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    service_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service_orders.id"), nullable=False
    )
    photo_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    uploaded_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    service_order: Mapped["ServiceOrder"] = relationship(
        "ServiceOrder", back_populates="photos"
    )
