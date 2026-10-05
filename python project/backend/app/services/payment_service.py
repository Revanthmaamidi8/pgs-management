from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.pg_property import PGProperty
from app.models.rent_record import RentRecord
from app.models.tenant import Tenant
from app.models.user import User


def list_payments(db: Session, current_user: User, pg_property_id: str | None = None, tenant_id: str | None = None) -> list[Payment]:
    query = db.query(Payment)

    if current_user.role.name != "SUPER_ADMIN":
        query = query.join(PGProperty).filter(PGProperty.owner_id == current_user.id)

    if pg_property_id:
        try:
            query = query.filter(Payment.pg_property_id == UUID(str(pg_property_id)))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    if tenant_id:
        try:
            query = query.filter(Payment.tenant_id == UUID(str(tenant_id)))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid tenant id") from exc

    return query.order_by(Payment.payment_date.desc()).all()


def create_payment(db: Session, current_user: User, payload) -> Payment:
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manage this PG payments")

    rent_record = None
    if payload.rent_record_id:
        try:
            rent_id = UUID(str(payload.rent_record_id))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid rent record id") from exc

        rent_record = db.query(RentRecord).filter(RentRecord.id == rent_id).first()
        if rent_record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rent record not found")
        if rent_record.tenant_id != tenant_id or rent_record.pg_property_id != pg_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rent record does not belong to this tenant and PG")

    payment = Payment(
        tenant_id=tenant_id,
        pg_property_id=pg_id,
        rent_record_id=rent_record.id if rent_record else None,
        amount=float(payload.amount),
        payment_date=payload.payment_date,
        payment_mode=payload.payment_mode,
        reference_number=payload.reference_number,
        notes=payload.notes,
        status="completed",
    )
    db.add(payment)
    db.flush()

    if rent_record is not None:
        rent_record.paid_amount = round(float(rent_record.paid_amount) + float(payload.amount), 2)
        if rent_record.paid_amount >= rent_record.amount:
            rent_record.status = "paid"
        elif rent_record.paid_amount > 0:
            rent_record.status = "partial"

    db.commit()
    db.refresh(payment)
    if rent_record is not None:
        db.refresh(rent_record)
    return payment
