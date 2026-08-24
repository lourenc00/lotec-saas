import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CompanyUser(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "company_users"
    __table_args__ = (
        UniqueConstraint("company_id", "user_id", name="uq_company_user"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="ADMIN")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")
    invited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    company: Mapped["Company"] = relationship("Company", back_populates="user_links")
    user: Mapped["User"] = relationship("User", back_populates="company_links")


from app.models.company import Company
from app.models.user import User
