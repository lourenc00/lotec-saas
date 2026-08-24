import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, SoftDeleteMixin


class Company(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    document: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address_line: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address_extra: Mapped[str | None] = mapped_column(String(100), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(12), nullable=True)
    logo_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")
    timezone: Mapped[str] = mapped_column(
        String(64), nullable=False, default="America/Sao_Paulo"
    )

    user_links: Mapped[list["CompanyUser"]] = relationship(
        "CompanyUser", back_populates="company", lazy="selectin"
    )
    customers: Mapped[list["Customer"]] = relationship(
        "Customer", back_populates="company", lazy="selectin"
    )
    subscription: Mapped["Subscription | None"] = relationship(
        "Subscription", back_populates="company", uselist=False, lazy="selectin"
    )


from app.models.company_user import CompanyUser
from app.models.customer import Customer
from app.models.subscription import Subscription
