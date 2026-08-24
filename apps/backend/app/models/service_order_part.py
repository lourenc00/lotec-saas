import uuid

from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ServiceOrderPart(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "service_order_parts"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    service_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service_orders.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    total_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    service_order: Mapped["ServiceOrder"] = relationship(
        "ServiceOrder", back_populates="parts"
    )
