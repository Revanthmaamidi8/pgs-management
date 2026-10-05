from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services.payment_service import create_payment, list_payments

router = APIRouter(prefix="/api/v1", tags=["payments"])


@router.get("/payments", response_model=list[PaymentOut])
def get_payments(
    pg_property_id: str | None = None,
    tenant_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_payments(db, current_user, pg_property_id=pg_property_id, tenant_id=tenant_id)


@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment_endpoint(
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_payment(db, current_user, payload)
