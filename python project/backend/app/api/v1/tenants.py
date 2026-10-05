from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.tenant import TenantCreate, TenantDetailsOut, TenantOut
from app.services.tenant_service import create_tenant, delete_tenant, get_tenant_by_id, list_tenants

router = APIRouter(prefix="/api/v1", tags=["tenants"])


@router.get("/tenants", response_model=list[TenantOut])
def get_tenants(
    pg_property_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_tenants(db, current_user, pg_property_id)


@router.get("/tenants/{tenant_id}", response_model=TenantDetailsOut)
def get_tenant_details(tenant_id: str, db: Session = Depends(get_db)):
    tenant = get_tenant_by_id(db, tenant_id)
    return {
        **TenantOut.model_validate(tenant).model_dump(),
        "pg_property_name": tenant.pg_property.name,
    }


@router.post("/tenants", response_model=TenantOut, status_code=status.HTTP_201_CREATED)
def create_tenant_endpoint(
    payload: TenantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_tenant(db, current_user, payload)


@router.delete("/tenants/{tenant_id}")
def delete_tenant_endpoint(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_tenant(db, current_user, tenant_id)
    return {"message": "Tenant and linked records were deleted."}
