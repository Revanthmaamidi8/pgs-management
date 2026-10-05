from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pg_property import PGProperty
from app.models.user import User


def list_pg_properties(db: Session, current_user: User) -> list[PGProperty]:
    if current_user.role.name == "SUPER_ADMIN":
        return db.query(PGProperty).all()
    return db.query(PGProperty).filter(PGProperty.owner_id == current_user.id).all()


def get_pg_property_or_404(db: Session, pg_id: str, current_user: User) -> PGProperty:
    try:
        pg = db.query(PGProperty).filter(PGProperty.id == UUID(pg_id)).first()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG property not found") from exc

    if pg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG property not found")

    if current_user.role.name != "SUPER_ADMIN" and pg.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this PG")

    return pg


def create_pg_property(db: Session, current_user: User, payload) -> PGProperty:
    if current_user.role.name not in {"SUPER_ADMIN", "OWNER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners or admins can create PGs")

    existing = (
        db.query(PGProperty)
        .filter(
            PGProperty.name == payload.name,
            PGProperty.city == payload.city,
            PGProperty.address == payload.address,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A PG with this name and address already exists")

    pg = PGProperty(
        name=payload.name,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        pincode=payload.pincode,
        contact_number=payload.contact_number,
        email=payload.email,
        number_of_floors=payload.number_of_floors,
        description=payload.description,
        facilities=payload.facilities,
        owner_id=current_user.id,
        is_active=True,
    )
    db.add(pg)
    db.commit()
    db.refresh(pg)
    return pg


def delete_pg_property(db: Session, current_user: User, pg_id: str) -> None:
    pg = get_pg_property_or_404(db, pg_id, current_user)
    if current_user.role.name not in {"SUPER_ADMIN", "OWNER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners or admins can delete PGs")

    db.delete(pg)
    db.commit()
