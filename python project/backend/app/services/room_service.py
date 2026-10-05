from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pg_property import PGProperty
from app.models.room import Room
from app.models.user import User


def list_rooms(db: Session, current_user: User, pg_property_id: str | None = None) -> list[Room]:
    query = db.query(Room)

    if current_user.role.name != "SUPER_ADMIN":
        query = query.join(PGProperty).filter(PGProperty.owner_id == current_user.id)

    if pg_property_id:
        try:
            query = query.filter(Room.pg_property_id == UUID(pg_property_id))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    return query.all()


def create_room(db: Session, current_user: User, payload) -> Room:
    try:
        pg_id = UUID(str(payload.pg_property_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    pg = db.query(PGProperty).filter(PGProperty.id == pg_id).first()
    if pg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG property not found")
    if current_user.role.name != "SUPER_ADMIN" and pg.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add a room to this PG")

    existing = db.query(Room).filter(Room.pg_property_id == pg_id, Room.room_number == payload.room_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A room with this number already exists in this PG")

    room = Room(
        pg_property_id=pg.id,
        room_number=payload.room_number,
        floor=payload.floor,
        room_type=payload.room_type,
        capacity=payload.capacity,
        monthly_rent=payload.monthly_rent,
        status=payload.status,
        description=payload.description,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room
