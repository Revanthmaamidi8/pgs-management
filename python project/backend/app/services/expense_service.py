from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.pg_property import PGProperty
from app.models.user import User


def list_expenses(db: Session, current_user: User, pg_property_id: str | None = None) -> list[Expense]:
    query = db.query(Expense)

    if current_user.role.name != "SUPER_ADMIN":
        query = query.join(PGProperty).filter(PGProperty.owner_id == current_user.id)

    if pg_property_id:
        try:
            query = query.filter(Expense.pg_property_id == UUID(str(pg_property_id)))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    return query.order_by(Expense.expense_date.desc()).all()


def create_expense(db: Session, current_user: User, payload) -> Expense:
    try:
        pg_id = UUID(str(payload.pg_property_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid PG property id") from exc

    pg = db.query(PGProperty).filter(PGProperty.id == pg_id).first()
    if pg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG property not found")

    if current_user.role.name != "SUPER_ADMIN" and pg.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to manage this PG expenses")

    expense = Expense(
        pg_property_id=pg_id,
        category=payload.category,
        description=payload.description,
        amount=float(payload.amount),
        expense_date=payload.expense_date,
        vendor=payload.vendor,
        payment_mode=payload.payment_mode,
        reference_number=payload.reference_number,
        notes=payload.notes,
        status="paid",
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense
