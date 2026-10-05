from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.deposit import DepositCreate, DepositOut
from app.services.deposit_service import create_deposit, list_deposits

router = APIRouter(prefix="/api/v1", tags=["deposits"])


@router.get("/deposits", response_model=list[DepositOut])
def get_deposits(
    pg_property_id: str | None = None,
    tenant_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_deposits(db, current_user, pg_property_id=pg_property_id, tenant_id=tenant_id)


@router.post("/deposits", response_model=DepositOut, status_code=status.HTTP_201_CREATED)
def create_deposit_endpoint(
    payload: DepositCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_deposit(db, current_user, payload)
