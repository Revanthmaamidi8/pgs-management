import uuid

from datetime import date

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BedAllocation(Base):
    __tablename__ = "bed_allocations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    bed_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("beds.id"), nullable=False)
    pg_property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_properties.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="allocations")
    bed: Mapped["Bed"] = relationship(back_populates="allocations")
    pg_property: Mapped["PGProperty"] = relationship(back_populates="allocations")
