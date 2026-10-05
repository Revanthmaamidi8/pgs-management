from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pg_property import PGProperty
from app.models.rent_record import RentRecord
from app.models.tenant import Tenant
from app.models.user import User


def list_rent_records(db: Session, current_user: User, pg_property_id: str | None = None, tenant_id: str | None = None) -> list[RentRecord]:
    query = db.query(RentRecord)

    if current_user.role.name != "SUPER_ADMIN":
        query = query.join(PGProperty).filter(PGProperty.owner_id == current_user.id)

    if pg_property_id:
        try:
            query = query.filter(RentRecord.pg_property_id == UUID(str(pg_property_id)))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    if tenant_id:
        try:
            query = query.filter(RentRecord.tenant_id == UUID(str(tenant_id)))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant id") from exc

    return query.order_by(RentRecord.month.desc()).all()


def create_rent_record(db: Session, current_user: User, payload) -> RentRecord:
    try:
        tenant_id = UUID(str(payload.tenant_id))
        pg_id = UUID(str(payload.pg_property_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant or PG id") from exc

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    pg = db.query(PGProperty).filter(PGProperty.id == pg_id).first()
    if pg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG property not found")

    if tenant.pg_property_id != pg_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant does not belong to this PG")

    if current_user.role.name != "SUPER_ADMIN" and pg.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manage this PG rent")

    existing = db.query(RentRecord).filter(RentRecord.tenant_id == tenant_id, RentRecord.month == payload.month).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rent record for this month already exists")

    rent_record = RentRecord(
        tenant_id=tenant_id,
        pg_property_id=pg_id,
        month=payload.month,
        amount=float(payload.amount),
        due_date=payload.due_date,
        notes=payload.notes,
        status="pending",
    )
    db.add(rent_record)
    db.commit()
    db.refresh(rent_record)
    return rent_record
