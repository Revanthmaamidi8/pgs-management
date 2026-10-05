from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.bed import BedCreate, BedOut
from app.services.bed_service import create_bed, list_beds

router = APIRouter(prefix="/api/v1", tags=["beds"])


@router.get("/beds", response_model=list[BedOut])
def get_beds(
    room_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_beds(db, current_user, room_id)


@router.post("/beds", response_model=BedOut, status_code=status.HTTP_201_CREATED)
def create_bed_endpoint(
    payload: BedCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_bed(db, current_user, payload)
