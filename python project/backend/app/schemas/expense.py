from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    pg_property_id: str
    category: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=2)
    amount: float = Field(..., gt=0)
    expense_date: date
    vendor: str | None = None
    payment_mode: str = Field(..., min_length=2, max_length=50)
    reference_number: str | None = None
    notes: str | None = None


class ExpenseOut(BaseModel):
    id: UUID
    pg_property_id: UUID
    category: str
    description: str
    amount: float
    expense_date: date
    vendor: str | None = None
    payment_mode: str
    reference_number: str | None = None
    status: str
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
