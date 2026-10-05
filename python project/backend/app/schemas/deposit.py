from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DepositCreate(BaseModel):
    tenant_id: str
    pg_property_id: str
    amount: float = Field(..., gt=0)
    deposit_date: date
    payment_mode: str = Field(..., min_length=2, max_length=50)
    reference_number: str | None = None
    notes: str | None = None


class DepositOut(BaseModel):
    id: UUID
    tenant_id: UUID
    pg_property_id: UUID
    amount: float
    deposit_date: date
    payment_mode: str
    reference_number: str | None = None
    status: str
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
