from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=180)
    document: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    document: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class CustomerResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    document: str | None
    phone: str | None
    whatsapp: str | None
    email: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
