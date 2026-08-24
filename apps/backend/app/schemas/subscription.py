from pydantic import BaseModel
from datetime import datetime
import uuid


class CheckoutRequest(BaseModel):
    plan_id: uuid.UUID


class ChangePlanRequest(BaseModel):
    plan_id: uuid.UUID


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    company_id: uuid.UUID
    plan_id: uuid.UUID
    status: str
    provider_status: str | None
    started_at: datetime | None
    trial_ends_at: datetime | None
    next_billing_date: datetime | None
    canceled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
