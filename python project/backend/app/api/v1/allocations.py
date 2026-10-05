from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.bed_allocation import BedAllocationCreate, BedAllocationOut
from app.services.allocation_service import create_allocation, list_allocations

router = APIRouter(prefix="/api/v1", tags=["allocations"])


@router.get("/allocations", response_model=list[BedAllocationOut])
def get_allocations(
    pg_property_id: str | None = None,
    tenant_id: str | None = None,
    bed_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_allocations(db, current_user, pg_property_id=pg_property_id, tenant_id=tenant_id, bed_id=bed_id)


@router.post("/allocations", response_model=BedAllocationOut, status_code=status.HTTP_201_CREATED)
def create_allocation_endpoint(
    payload: BedAllocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_allocation(db, current_user, payload)
