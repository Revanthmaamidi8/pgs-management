import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PGProperty(Base):
    __tablename__ = "pg_properties"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_number: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    number_of_floors: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    facilities: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    owner: Mapped["User"] = relationship(back_populates="pg_properties")
    rooms: Mapped[list["Room"]] = relationship(back_populates="pg_property", cascade="all, delete-orphan")
    tenants: Mapped[list["Tenant"]] = relationship(back_populates="pg_property", cascade="all, delete-orphan")
    allocations: Mapped[list["BedAllocation"]] = relationship(back_populates="pg_property", cascade="all, delete-orphan")
    rent_records: Mapped[list["RentRecord"]] = relationship(back_populates="pg_property", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship(back_populates="pg_property", cascade="all, delete-orphan")
    deposits: Mapped[list["Deposit"]] = relationship(back_populates="pg_property", cascade="all, delete-orphan")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="pg_property", cascade="all, delete-orphan")
