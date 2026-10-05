from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.rent_record import RentRecordCreate, RentRecordOut
from app.services.rent_service import create_rent_record, list_rent_records

router = APIRouter(prefix="/api/v1", tags=["rent-records"])


@router.get("/rent-records", response_model=list[RentRecordOut])
def get_rent_records(
    pg_property_id: str | None = None,
    tenant_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_rent_records(db, current_user, pg_property_id=pg_property_id, tenant_id=tenant_id)


@router.post("/rent-records", response_model=RentRecordOut, status_code=status.HTTP_201_CREATED)
def create_rent_record_endpoint(
    payload: RentRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_rent_record(db, current_user, payload)
