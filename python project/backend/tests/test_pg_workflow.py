import uuid

import pytest
from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models import Bed, BedAllocation, Deposit, Expense, Payment, PGProperty, RentRecord, Room, Tenant, User

client = TestClient(app)


@pytest.fixture
def workflow_cleanup():
    identifiers = {}
    yield identifiers

    db = SessionLocal()
    try:
        pg_id = identifiers.get("pg_id")
        if pg_id:
            room_ids = [row.id for row in db.query(Room.id).filter(Room.pg_property_id == uuid.UUID(pg_id)).all()]
            for model in (Payment, Deposit, Expense, BedAllocation, RentRecord):
                db.query(model).filter(model.pg_property_id == uuid.UUID(pg_id)).delete(synchronize_session=False)
            if room_ids:
                db.query(Bed).filter(Bed.room_id.in_(room_ids)).delete(synchronize_session=False)
            db.query(Tenant).filter(Tenant.pg_property_id == uuid.UUID(pg_id)).delete(synchronize_session=False)
            db.query(Room).filter(Room.pg_property_id == uuid.UUID(pg_id)).delete(synchronize_session=False)
            db.query(PGProperty).filter(PGProperty.id == uuid.UUID(pg_id)).delete(synchronize_session=False)

        owner_username = identifiers.get("owner_username")
        if owner_username:
            owner = db.query(User).filter(User.username == owner_username).first()
            if owner:
                db.delete(owner)
        db.commit()
    finally:
        db.close()


def create_owner_and_token():
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"owner{suffix}",
        "email": f"owner{suffix}@example.com",
        "full_name": "Test Owner",
        "password": "StrongPass123!",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": payload["username"], "password": payload["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]
    return token, payload["username"]


def test_pg_room_bed_and_tenant_flow(workflow_cleanup):
    token, owner_username = create_owner_and_token()
    workflow_cleanup["owner_username"] = owner_username
    headers = {"Authorization": f"Bearer {token}"}
    suffix = uuid.uuid4().hex[:8]

    pg_response = client.post(
        "/api/v1/pgs",
        json={
            "name": f"Sunrise PG {suffix}",
            "address": f"MG Road {suffix}",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560001",
            "contact_number": "+919876543210",
            "email": f"sunrise{suffix}@example.com",
            "number_of_floors": 3,
            "description": "Premium PG",
            "facilities": ["Wi-Fi", "Laundry", "Food"],
        },
        headers=headers,
    )
    assert pg_response.status_code == 201, pg_response.text
    pg_id = pg_response.json()["id"]
    workflow_cleanup["pg_id"] = pg_id

    room_response = client.post(
        "/api/v1/rooms",
        json={
            "pg_property_id": pg_id,
            "room_number": "101",
            "floor": 1,
            "room_type": "Single",
            "capacity": 1,
            "monthly_rent": 9000,
            "status": "available",
            "description": "Front-facing room",
        },
        headers=headers,
    )
    assert room_response.status_code == 201, room_response.text
    room_id = room_response.json()["id"]

    bed_response = client.post(
        "/api/v1/beds",
        json={
            "room_id": room_id,
            "bed_number": "A",
            "status": "available",
        },
        headers=headers,
    )
    assert bed_response.status_code == 201, bed_response.text
    bed_id = bed_response.json()["id"]

    beds_response = client.get("/api/v1/beds", headers=headers)
    assert beds_response.status_code == 200, beds_response.text
    assert [bed["id"] for bed in beds_response.json()] == [bed_id]

    tenant_response = client.post(
        "/api/v1/tenants",
        json={
            "pg_property_id": pg_id,
            "full_name": f"Ravi Kumar {suffix}",
            "phone_number": f"+9199001122{suffix[-3:]}",
            "email": f"ravi{suffix}@example.com",
            "date_of_birth": "1995-06-12",
            "gender": "male",
            "address": "Jayanagar, Bengaluru",
            "emergency_contact": "Mother",
            "emergency_phone": "+919988776655",
            "government_id_type": "Aadhaar",
            "government_id_number": f"1234 5678 90{suffix[-2:]}",
            "joining_date": "2025-01-10",
            "expected_leaving_date": "2026-01-10",
            "deposit_amount": 20000,
            "status": "active",
        },
        headers=headers,
    )
    assert tenant_response.status_code == 201, tenant_response.text
    tenant_id = tenant_response.json()["id"]
    assert len(tenant_id) == 36

    tenant_details_response = client.get(f"/api/v1/tenants/{tenant_id}")
    assert tenant_details_response.status_code == 200, tenant_details_response.text
    assert tenant_details_response.json()["id"] == tenant_id
    assert tenant_details_response.json()["full_name"] == f"Ravi Kumar {suffix}"
    assert tenant_details_response.json()["government_id_number"] == f"1234 5678 90{suffix[-2:]}"
    assert tenant_details_response.json()["pg_property_name"] == f"Sunrise PG {suffix}"

    allocation_response = client.post(
        "/api/v1/allocations",
        json={
            "tenant_id": tenant_id,
            "bed_id": bed_id,
            "pg_property_id": pg_id,
            "start_date": "2025-01-10",
        },
        headers=headers,
    )
    assert allocation_response.status_code == 201, allocation_response.text
    assert allocation_response.json()["tenant_id"] == tenant_id
    assert allocation_response.json()["bed_id"] == bed_id

    allocations_response = client.get("/api/v1/allocations", headers=headers)
    assert allocations_response.status_code == 200, allocations_response.text
    assert any(item["id"] == allocation_response.json()["id"] for item in allocations_response.json())

    tenant_delete_response = client.delete(f"/api/v1/tenants/{tenant_id}", headers=headers)
    assert tenant_delete_response.status_code == 200, tenant_delete_response.text
    assert client.get(f"/api/v1/tenants/{tenant_id}").status_code == 404

    pg_delete_response = client.delete(f"/api/v1/pgs/{pg_id}", headers=headers)
    assert pg_delete_response.status_code == 200, pg_delete_response.text
    assert client.get(f"/api/v1/pgs/{pg_id}", headers=headers).status_code == 404
