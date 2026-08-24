from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class DeviceCreate(BaseModel):
    customer_id: uuid.UUID
    category: str = Field(..., max_length=50)
    brand: str | None = None
    model: str = Field(..., min_length=1, max_length=150)
    color: str | None = None
    imei: str | None = None
    serial_number: str | None = None
    physical_condition: str | None = None
    notes: str | None = None


class DeviceUpdate(BaseModel):
    category: str | None = None
    brand: str | None = None
    model: str | None = None
    color: str | None = None
    imei: str | None = None
    serial_number: str | None = None
    physical_condition: str | None = None
    notes: str | None = None


class DeviceResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    customer_id: uuid.UUID
    category: str
    brand: str | None
    model: str
    color: str | None
    imei: str | None
    serial_number: str | None
    physical_condition: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
