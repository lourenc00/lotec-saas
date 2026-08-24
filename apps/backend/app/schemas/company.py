from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    legal_name: str | None = None
    document: str | None = None
    email: str | None = None
    phone: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    document: str | None = None
    email: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    address_line: str | None = None
    address_number: str | None = None
    address_extra: str | None = None
    district: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    legal_name: str | None
    document: str | None
    email: str | None
    phone: str | None
    status: str
    timezone: str
    created_at: datetime

    model_config = {"from_attributes": True}
