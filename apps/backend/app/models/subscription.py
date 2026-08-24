import uuid

from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Subscription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="mercadopago"
    )
    provider_subscription_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    provider_payer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="TRIAL")
    provider_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    started_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trial_ends_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_billing_date: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    past_due_since: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    grace_period_ends_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    canceled_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ended_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    company: Mapped["Company"] = relationship("Company", back_populates="subscription")
    plan: Mapped["Plan"] = relationship("Plan", lazy="selectin")


class WebhookEvent(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "webhook_events"

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    event_key: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signature_valid: Mapped[bool] = mapped_column(nullable=False, default=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    headers_sanitized: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(30), nullable=False)
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    processed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class Payment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "payments"

    company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    provider_status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BRL")
    paid_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    due_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)


from app.models.plan import Plan
from app.models.company import Company
