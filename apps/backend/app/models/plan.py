import uuid

from sqlalchemy import String, Text, Boolean, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Plan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plans"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_monthly: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    mercadopago_plan_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    features: Mapped[list["PlanFeature"]] = relationship(
        "PlanFeature", back_populates="plan", lazy="selectin"
    )


class Feature(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "features"

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_type: Mapped[str] = mapped_column(String(20), nullable=False)


class PlanFeature(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "plan_features"

    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False
    )
    feature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("features.id"), nullable=False
    )
    bool_value: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    int_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    string_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="features")
    feature: Mapped["Feature"] = relationship("Feature")
