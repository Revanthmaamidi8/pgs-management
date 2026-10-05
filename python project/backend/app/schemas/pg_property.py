from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class PGPropertyCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    address: str = Field(..., min_length=5, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=4, max_length=20)
    contact_number: str = Field(..., min_length=8, max_length=30)
    email: EmailStr
    number_of_floors: int = Field(default=1, ge=1)
    description: str | None = None
    facilities: list[str] = Field(default_factory=list)


class PGPropertyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    address: str | None = Field(default=None, min_length=5, max_length=255)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=100)
    pincode: str | None = Field(default=None, min_length=4, max_length=20)
    contact_number: str | None = Field(default=None, min_length=8, max_length=30)
    email: EmailStr | None = None
    number_of_floors: int | None = Field(default=None, ge=1)
    description: str | None = None
    facilities: list[str] | None = None
    is_active: bool | None = None


class PGPropertyOut(BaseModel):
    id: UUID
    name: str
    address: str
    city: str
    state: str
    pincode: str
    contact_number: str
    email: str
    number_of_floors: int
    description: str | None = None
    facilities: list[str] = []
    owner_id: UUID
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
