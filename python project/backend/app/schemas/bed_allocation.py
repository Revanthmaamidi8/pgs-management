from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class BedAllocationCreate(BaseModel):
    tenant_id: str
    bed_id: str
    pg_property_id: str
    start_date: date
    end_date: date | None = None
    notes: str | None = None


class BedAllocationOut(BaseModel):
    id: UUID
    tenant_id: UUID
    bed_id: UUID
    pg_property_id: UUID
    start_date: date
    end_date: date | None = None
    status: str
    is_active: bool
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
