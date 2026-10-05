from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TenantCreate(BaseModel):
    pg_property_id: str
    full_name: str = Field(..., min_length=2, max_length=200)
    phone_number: str = Field(..., min_length=8, max_length=30)
    email: EmailStr | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    government_id_type: str | None = None
    government_id_number: str | None = None
    joining_date: date
    expected_leaving_date: date | None = None
    actual_leaving_date: date | None = None
    deposit_amount: float = Field(default=0.0, ge=0)
    status: str = Field(default="active", min_length=2, max_length=50)


class TenantOut(BaseModel):
    id: UUID
    pg_property_id: UUID
    full_name: str
    profile_photo: str | None = None
    phone_number: str
    email: str | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    emergency_phone: str | None = None
    government_id_type: str | None = None
    government_id_number: str | None = None
    joining_date: date
    expected_leaving_date: date | None = None
    actual_leaving_date: date | None = None
    deposit_amount: float
    status: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TenantDetailsOut(TenantOut):
    pg_property_name: str
