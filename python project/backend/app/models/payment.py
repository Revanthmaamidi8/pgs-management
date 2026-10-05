import uuid

from datetime import date

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    pg_property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_properties.id"), nullable=False)
    rent_record_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("rent_records.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="completed", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="payments")
    pg_property: Mapped["PGProperty"] = relationship(back_populates="payments")
    rent_record: Mapped["RentRecord | None"] = relationship(back_populates="payments")
