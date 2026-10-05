from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RentRecordCreate(BaseModel):
    tenant_id: str
    pg_property_id: str
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    amount: float = Field(..., gt=0)
    due_date: date | None = None
    notes: str | None = None


class RentRecordOut(BaseModel):
    id: UUID
    tenant_id: UUID
    pg_property_id: UUID
    month: str
    amount: float
    paid_amount: float
    due_date: date | None = None
    status: str
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
