from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    pg_property_id: str
    room_number: str = Field(..., min_length=1, max_length=50)
    floor: int = Field(..., ge=0)
    room_type: str = Field(..., min_length=2, max_length=50)
    capacity: int = Field(..., ge=1)
    monthly_rent: float = Field(..., ge=0)
    status: str = Field(default="available", min_length=2, max_length=50)
    description: str | None = None


class RoomOut(BaseModel):
    id: UUID
    pg_property_id: UUID
    room_number: str
    floor: int
    room_type: str
    capacity: int
    monthly_rent: float
    status: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
