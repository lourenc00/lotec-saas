from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class ServiceOrderServiceCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(default=1, ge=0)
    unit_price: float = Field(default=0, ge=0)


class ServiceOrderServiceUpdate(BaseModel):
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None


class ServiceOrderServiceResponse(BaseModel):
    id: uuid.UUID
    description: str
    quantity: float
    unit_price: float
    total_price: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ServiceOrderPartCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(default=1, ge=0)
    unit_price: float = Field(default=0, ge=0)


class ServiceOrderPartUpdate(BaseModel):
    description: str | None = None
    quantity: float | None = None
    unit_price: float | None = None


class ServiceOrderPartResponse(BaseModel):
    id: uuid.UUID
    description: str
    quantity: float
    unit_price: float
    total_price: float
    created_at: datetime

    model_config = {"from_attributes": True}


class ServiceOrderCreate(BaseModel):
    customer_id: uuid.UUID
    device_id: uuid.UUID
    problem_reported: str = Field(..., min_length=1)
    service_requested: str | None = None
    estimated_delivery_at: datetime | None = None
    responsible_user_id: uuid.UUID | None = None
    estimated_value: float | None = None
    services: list[ServiceOrderServiceCreate] = []
    parts: list[ServiceOrderPartCreate] = []


class ServiceOrderUpdate(BaseModel):
    problem_reported: str | None = None
    service_requested: str | None = None
    diagnosis: str | None = None
    service_performed_summary: str | None = None
    internal_notes: str | None = None
    customer_notes: str | None = None
    estimated_delivery_at: datetime | None = None
    responsible_user_id: uuid.UUID | None = None
    estimated_value: float | None = None
    approved_value: float | None = None
    discount: float | None = None
    payment_method: str | None = None
    payment_status: str | None = None


class ServiceOrderStatusChange(BaseModel):
    status: str = Field(..., max_length=30)
    notes: str | None = None


class ServiceOrderResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    os_number: int
    customer_id: uuid.UUID
    device_id: uuid.UUID
    responsible_user_id: uuid.UUID | None
    status: str
    entry_at: datetime | None
    estimated_delivery_at: datetime | None
    completion_at: datetime | None
    delivery_at: datetime | None
    problem_reported: str
    service_requested: str | None
    diagnosis: str | None
    service_performed_summary: str | None
    internal_notes: str | None
    customer_notes: str | None
    estimated_value: float | None
    approved_value: float | None
    discount: float
    final_value: float | None
    payment_method: str | None
    payment_status: str | None
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceOrderListResponse(BaseModel):
    items: list[ServiceOrderResponse]
    page: int
    page_size: int
    total: int
    pages: int
