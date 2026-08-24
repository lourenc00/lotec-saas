import uuid

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SystemSetting(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
