from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bed import Bed
from app.models.pg_property import PGProperty
from app.models.room import Room
from app.models.user import User


def list_beds(db: Session, current_user: User, room_id: str | None = None) -> list[Bed]:
    query = db.query(Bed).join(Room)

    if current_user.role.name != "SUPER_ADMIN":
        query = query.join(PGProperty, Room.pg_property_id == PGProperty.id).filter(
            PGProperty.owner_id == current_user.id
        )

    if room_id:
        try:
            query = query.filter(Bed.room_id == UUID(room_id))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room id") from exc

    return query.all()


def create_bed(db: Session, current_user: User, payload) -> Bed:
    try:
        room_id = UUID(str(payload.room_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room id") from exc

    room = db.query(Room).filter(Room.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    if current_user.role.name != "SUPER_ADMIN" and room.pg_property.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add a bed to this room")

    existing = db.query(Bed).filter(Bed.room_id == room_id, Bed.bed_number == payload.bed_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A bed with this number already exists in this room")

    bed = Bed(room_id=room.id, bed_number=payload.bed_number, status=payload.status)
    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed
