from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseOut
from app.services.expense_service import create_expense, list_expenses

router = APIRouter(prefix="/api/v1", tags=["expenses"])


@router.get("/expenses", response_model=list[ExpenseOut])
def get_expenses(
    pg_property_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_expenses(db, current_user, pg_property_id=pg_property_id)


@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense_endpoint(
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_expense(db, current_user, payload)
