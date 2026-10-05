import uuid

from datetime import date

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pg_property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_properties.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    vendor: Mapped[str | None] = mapped_column(String(200), nullable=True)
    payment_mode: Mapped[str] = mapped_column(String(50), nullable=False)
    reference_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="paid", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    pg_property: Mapped["PGProperty"] = relationship(back_populates="expenses")
