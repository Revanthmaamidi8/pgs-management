import uuid

from datetime import date

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pg_property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_properties.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    profile_photo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(String(200), nullable=True)
    emergency_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    government_id_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    government_id_number: Mapped[str | None] = mapped_column(String(200), nullable=True)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_leaving_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_leaving_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    deposit_amount: Mapped[float] = mapped_column(default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    pg_property: Mapped["PGProperty"] = relationship(back_populates="tenants")
    allocations: Mapped[list["BedAllocation"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    rent_records: Mapped[list["RentRecord"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    deposits: Mapped[list["Deposit"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
