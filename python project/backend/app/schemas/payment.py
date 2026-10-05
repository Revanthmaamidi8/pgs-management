from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    tenant_id: str
    pg_property_id: str
    rent_record_id: str | None = None
    amount: float = Field(..., gt=0)
    payment_date: date
    payment_mode: str = Field(..., min_length=2, max_length=50)
    reference_number: str | None = None
    notes: str | None = None


class PaymentOut(BaseModel):
    id: UUID
    tenant_id: UUID
    pg_property_id: UUID
    rent_record_id: UUID | None = None
    amount: float
    payment_date: date
    payment_mode: str
    reference_number: str | None = None
    status: str
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
