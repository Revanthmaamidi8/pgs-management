from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.pg_property import PGProperty
from app.models.tenant import Tenant
from app.models.user import User


def list_tenants(db: Session, current_user: User, pg_property_id: str | None = None) -> list[Tenant]:
    query = db.query(Tenant)

    if current_user.role.name != "SUPER_ADMIN":
        query = query.filter(Tenant.pg_property_id.in_([pg.id for pg in current_user.pg_properties]))

    if pg_property_id:
        try:
            query = query.filter(Tenant.pg_property_id == UUID(pg_property_id))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    return query.all()


def get_tenant_by_id(db: Session, tenant_id: str) -> Tenant:
    try:
        tenant_uuid = UUID(tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant ID") from exc

    tenant = db.query(Tenant).filter(Tenant.id == tenant_uuid).first()
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant


def create_tenant(db: Session, current_user: User, payload) -> Tenant:
    try:
        pg_id = UUID(str(payload.pg_property_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    pg = db.query(PGProperty).filter(PGProperty.id == pg_id).first()
    if pg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG property not found")

    if current_user.role.name != "SUPER_ADMIN" and pg.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add tenants to this PG")

    if payload.email:
        existing = db.query(Tenant).filter(Tenant.email == str(payload.email)).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A tenant with this email already exists")

    tenant = Tenant(
        pg_property_id=pg.id,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        email=str(payload.email) if payload.email else None,
        date_of_birth=payload.date_of_birth,
        gender=payload.gender,
        address=payload.address,
        emergency_contact=payload.emergency_contact,
        emergency_phone=payload.emergency_phone,
        government_id_type=payload.government_id_type,
        government_id_number=payload.government_id_number,
        joining_date=payload.joining_date,
        expected_leaving_date=payload.expected_leaving_date,
        actual_leaving_date=payload.actual_leaving_date,
        deposit_amount=payload.deposit_amount,
        status=payload.status,
        is_active=True,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def delete_tenant(db: Session, current_user: User, tenant_id: str) -> None:
    tenant = get_tenant_by_id(db, tenant_id)
    if current_user.role.name != "SUPER_ADMIN" and tenant.pg_property.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this tenant")

    db.delete(tenant)
    db.commit()
