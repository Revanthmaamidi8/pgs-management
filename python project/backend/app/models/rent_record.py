import uuid

from datetime import date

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RentRecord(Base):
    __tablename__ = "rent_records"
    __table_args__ = (UniqueConstraint("tenant_id", "month", name="uq_rent_record_tenant_month"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    pg_property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_properties.id"), nullable=False)
    month: Mapped[str] = mapped_column(String(7), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    paid_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="rent_records")
    pg_property: Mapped["PGProperty"] = relationship(back_populates="rent_records")
    payments: Mapped[list["Payment"]] = relationship(back_populates="rent_record", cascade="all, delete-orphan")
