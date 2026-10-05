from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.pg_property import PGPropertyCreate, PGPropertyOut, PGPropertyUpdate
from app.services.pg_service import create_pg_property, delete_pg_property, get_pg_property_or_404, list_pg_properties

router = APIRouter(prefix="/api/v1", tags=["pgs"])


@router.get("/pgs", response_model=list[PGPropertyOut])
def get_pgs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_pg_properties(db, current_user)


@router.post("/pgs", response_model=PGPropertyOut, status_code=status.HTTP_201_CREATED)
def create_pg(
    payload: PGPropertyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_pg_property(db, current_user, payload)


@router.get("/pgs/{pg_id}", response_model=PGPropertyOut)
def get_pg(pg_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_pg_property_or_404(db, pg_id, current_user)


@router.put("/pgs/{pg_id}", response_model=PGPropertyOut)
def update_pg(
    pg_id: str,
    payload: PGPropertyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pg = get_pg_property_or_404(db, pg_id, current_user)
    if current_user.role.name not in {"SUPER_ADMIN", "OWNER"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this PG")
    if current_user.role.name != "SUPER_ADMIN" and pg.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this PG")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(pg, field, value)

    db.commit()
    db.refresh(pg)
    return pg


@router.delete("/pgs/{pg_id}")
def delete_pg(
    pg_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_pg_property(db, current_user, pg_id)
    return {"message": "PG and its linked records were deleted."}
