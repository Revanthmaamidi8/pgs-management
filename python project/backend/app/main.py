from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.allocations import router as allocations_router
from app.api.v1.auth import router as auth_router
from app.api.v1.beds import router as beds_router
from app.api.v1.deposits import router as deposits_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.payments import router as payments_router
from app.api.v1.pgs import router as pgs_router
from app.api.v1.rent_records import router as rent_records_router
from app.api.v1.rooms import router as rooms_router
from app.api.v1.tenants import router as tenants_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.models import Bed, BedAllocation, Deposit, Expense, Payment, PGProperty, RentRecord, Role, Room, Tenant, User  # noqa: F401
from app.services.auth_service import ensure_default_roles

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        ensure_default_roles(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(pgs_router)
app.include_router(rooms_router)
app.include_router(beds_router)
app.include_router(tenants_router)
app.include_router(allocations_router)
app.include_router(rent_records_router)
app.include_router(payments_router)
app.include_router(deposits_router)
app.include_router(expenses_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
