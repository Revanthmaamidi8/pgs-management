from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BedCreate(BaseModel):
    room_id: str
    bed_number: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="available", min_length=2, max_length=50)


class BedOut(BaseModel):
    id: UUID
    room_id: UUID
    bed_number: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
