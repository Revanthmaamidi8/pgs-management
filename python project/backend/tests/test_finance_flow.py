import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_owner_and_token():
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"financeowner{suffix}",
        "email": f"financeowner{suffix}@example.com",
        "full_name": "Finance Owner",
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


def test_rent_and_payment_flow():
    token = create_owner_and_token()
    headers = {"Authorization": f"Bearer {token}"}
    suffix = uuid.uuid4().hex[:8]

    pg_response = client.post(
        "/api/v1/pgs",
        json={
            "name": f"Finance PG {suffix}",
            "address": f"Finance Road {suffix}",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560001",
            "contact_number": "+919876543219",
            "email": f"finance{suffix}@example.com",
            "number_of_floors": 2,
            "description": "Finance PG",
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
            "room_number": "201",
            "floor": 2,
            "room_type": "Double",
            "capacity": 2,
            "monthly_rent": 12000,
            "status": "available",
            "description": "Finance room",
        },
        headers=headers,
    )
    assert room_response.status_code == 201, room_response.text
    room_id = room_response.json()["id"]

    bed_response = client.post(
        "/api/v1/beds",
        json={
            "room_id": room_id,
            "bed_number": "B",
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
            "full_name": f"Finance Tenant {suffix}",
            "phone_number": f"+919900112{suffix[-3:]}",
            "email": f"tenantfinance{suffix}@example.com",
            "date_of_birth": "1996-02-05",
            "gender": "male",
            "address": "Koramangala, Bengaluru",
            "emergency_contact": "Sister",
            "emergency_phone": "+919988776611",
            "government_id_type": "PAN",
            "government_id_number": f"ABCDE{suffix[-4:]}FGH",
            "joining_date": "2025-01-10",
            "expected_leaving_date": "2026-01-10",
            "deposit_amount": 25000,
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
            "start_date": "2025-01-10",
        },
        headers=headers,
    )
    assert allocation_response.status_code == 201, allocation_response.text

    rent_response = client.post(
        "/api/v1/rent-records",
        json={
            "tenant_id": tenant_id,
            "pg_property_id": pg_id,
            "month": "2025-01",
            "amount": 12000,
            "due_date": "2025-01-05",
            "notes": "January rent",
        },
        headers=headers,
    )
    assert rent_response.status_code == 201, rent_response.text
    rent_id = rent_response.json()["id"]

    payment_response = client.post(
        "/api/v1/payments",
        json={
            "tenant_id": tenant_id,
            "pg_property_id": pg_id,
            "rent_record_id": rent_id,
            "amount": 12000,
            "payment_date": "2025-01-04",
            "payment_mode": "UPI",
            "reference_number": "UPI-12345",
            "notes": "Paid via UPI",
        },
        headers=headers,
    )
    assert payment_response.status_code == 201, payment_response.text
    assert payment_response.json()["amount"] == 12000
