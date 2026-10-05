from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.room import RoomCreate, RoomOut
from app.services.room_service import create_room, list_rooms

router = APIRouter(prefix="/api/v1", tags=["rooms"])


@router.get("/rooms", response_model=list[RoomOut])
def get_rooms(
    pg_property_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_rooms(db, current_user, pg_property_id)


@router.post("/rooms", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room_endpoint(
    payload: RoomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_room(db, current_user, payload)
