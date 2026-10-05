import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_owner_and_token():
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"depexpowner{suffix}",
        "email": f"depexpowner{suffix}@example.com",
        "full_name": "Deposit Expense Owner",
        "password": "StrongPass123!",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 201, register_response.text

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": payload["username"], "password": payload["password"]},
    )
    assert login_response.status_code == 200, login_response.text
    return login_response.json()["access_token"]


def test_deposit_and_expense_flow():
    token = create_owner_and_token()
    headers = {"Authorization": f"Bearer {token}"}
    suffix = uuid.uuid4().hex[:8]

    pg_response = client.post(
        "/api/v1/pgs",
        json={
            "name": f"Deposit PG {suffix}",
            "address": f"Deposit Road {suffix}",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560001",
            "contact_number": "+919876543220",
            "email": f"deposit{suffix}@example.com",
            "number_of_floors": 2,
            "description": "Deposit test PG",
            "facilities": ["Wi-Fi"],
        },
        headers=headers,
    )
    assert pg_response.status_code == 201, pg_response.text
    pg_id = pg_response.json()["id"]

    room_response = client.post(
        "/api/v1/rooms",
        json={
            "pg_property_id": pg_id,
            "room_number": "301",
            "floor": 3,
            "room_type": "Shared",
            "capacity": 3,
            "monthly_rent": 8000,
            "status": "available",
            "description": "Deposit room",
        },
        headers=headers,
    )
    assert room_response.status_code == 201, room_response.text
    room_id = room_response.json()["id"]

    bed_response = client.post(
        "/api/v1/beds",
        json={
            "room_id": room_id,
            "bed_number": "C",
            "status": "available",
        },
        headers=headers,
    )
    assert bed_response.status_code == 201, bed_response.text
    bed_id = bed_response.json()["id"]

    tenant_response = client.post(
        "/api/v1/tenants",
        json={
            "pg_property_id": pg_id,
            "full_name": f"Deposit Tenant {suffix}",
            "phone_number": f"+919900112{suffix[-3:]}",
            "email": f"tenantdeposit{suffix}@example.com",
            "date_of_birth": "1994-08-15",
            "gender": "female",
            "address": "HSR Layout, Bengaluru",
            "emergency_contact": "Brother",
            "emergency_phone": "+919988776612",
            "government_id_type": "Aadhaar",
            "government_id_number": f"9876 5432 10{suffix[-2:]}",
            "joining_date": "2025-02-10",
            "expected_leaving_date": "2026-02-10",
            "deposit_amount": 18000,
            "status": "active",
        },
        headers=headers,
    )
    assert tenant_response.status_code == 201, tenant_response.text
    tenant_id = tenant_response.json()["id"]

    allocation_response = client.post(
        "/api/v1/allocations",
        json={
            "tenant_id": tenant_id,
            "bed_id": bed_id,
            "pg_property_id": pg_id,
            "start_date": "2025-02-10",
        },
        headers=headers,
    )
    assert allocation_response.status_code == 201, allocation_response.text

    deposit_response = client.post(
        "/api/v1/deposits",
        json={
            "tenant_id": tenant_id,
            "pg_property_id": pg_id,
            "amount": 18000,
            "deposit_date": "2025-02-10",
            "payment_mode": "UPI",
            "reference_number": "DEP-001",
            "notes": "Security deposit",
        },
        headers=headers,
    )
    assert deposit_response.status_code == 201, deposit_response.text
    assert deposit_response.json()["amount"] == 18000

    expense_response = client.post(
        "/api/v1/expenses",
        json={
            "pg_property_id": pg_id,
            "category": "Electricity",
            "description": "Monthly electricity bill",
            "amount": 2800,
            "expense_date": "2025-02-12",
            "vendor": "BESCOM",
            "payment_mode": "UPI",
            "reference_number": "EXP-001",
            "notes": "Power bill for February",
        },
        headers=headers,
    )
    assert expense_response.status_code == 201, expense_response.text
    assert expense_response.json()["amount"] == 2800
