import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Room(Base):
    __tablename__ = "rooms"
    __table_args__ = (UniqueConstraint("pg_property_id", "room_number", name="uq_room_pg_room_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pg_property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pg_properties.id"), nullable=False)
    room_number: Mapped[str] = mapped_column(String(50), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    room_type: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_rent: Mapped[float] = mapped_column(nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="available", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    pg_property: Mapped["PGProperty"] = relationship(back_populates="rooms")
    beds: Mapped[list["Bed"]] = relationship(back_populates="room", cascade="all, delete-orphan")
