from datetime import date
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bed import Bed
from app.models.bed_allocation import BedAllocation
from app.models.pg_property import PGProperty
from app.models.tenant import Tenant
from app.models.user import User


def list_allocations(
    db: Session,
    current_user: User,
    pg_property_id: str | None = None,
    tenant_id: str | None = None,
    bed_id: str | None = None,
) -> list[BedAllocation]:
    query = db.query(BedAllocation)

    if current_user.role.name != "SUPER_ADMIN":
        query = query.join(PGProperty, BedAllocation.pg_property_id == PGProperty.id).filter(PGProperty.owner_id == current_user.id)

    if pg_property_id:
        try:
            query = query.filter(BedAllocation.pg_property_id == UUID(str(pg_property_id)))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    if tenant_id:
        try:
            query = query.filter(BedAllocation.tenant_id == UUID(str(tenant_id)))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant id") from exc

    if bed_id:
        try:
            query = query.filter(BedAllocation.bed_id == UUID(str(bed_id)))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid bed id") from exc

    return query.order_by(BedAllocation.start_date.desc()).all()


def create_allocation(db: Session, current_user: User, payload) -> BedAllocation:
    try:
        tenant_id = UUID(str(payload.tenant_id))
        bed_id = UUID(str(payload.bed_id))
        pg_property_id = UUID(str(payload.pg_property_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid allocation id") from exc

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if bed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bed not found")

    if tenant.pg_property_id != pg_property_id or bed.room.pg_property_id != pg_property_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant and bed must belong to the same PG")

    if current_user.role.name != "SUPER_ADMIN" and tenant.pg_property.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to allocate this bed")

    active_bed_allocation = (
        db.query(BedAllocation)
        .filter(BedAllocation.bed_id == bed_id, BedAllocation.is_active.is_(True))
        .first()
    )
    if active_bed_allocation:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This bed already has an active tenant")

    active_tenant_allocation = (
        db.query(BedAllocation)
        .filter(BedAllocation.tenant_id == tenant_id, BedAllocation.is_active.is_(True))
        .first()
    )
    if active_tenant_allocation:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This tenant already has an active bed allocation")

    if bed.status != "available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only available beds can be assigned")

    allocation = BedAllocation(
        tenant_id=tenant.id,
        bed_id=bed.id,
        pg_property_id=pg_property_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status="active",
        is_active=True,
        notes=payload.notes,
    )
    bed.status = "occupied"
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    return allocation
