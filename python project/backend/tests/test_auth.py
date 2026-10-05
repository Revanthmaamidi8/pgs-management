import uuid

from fastapi.testclient import TestClient

from app.db.session import SessionLocal
from app.main import app
from app.models import User

client = TestClient(app)


def test_register_and_login_flow():
    suffix = uuid.uuid4().hex[:8]
    payload = {
        "username": f"tenantowner{suffix}",
        "email": f"tenantowner{suffix}@example.com",
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

    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token_data['access_token']}"},
    )
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["username"] == payload["username"]

    db = SessionLocal()
    try:
        registered_user = db.query(User).filter(
            User.username == payload["username"], User.email == payload["email"]
        ).first()
        if registered_user:
            db.delete(registered_user)
            db.commit()
    finally:
        db.close()


def test_unknown_login_does_not_create_account():
    username = f"missing-{uuid.uuid4().hex}"
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": username, "password": "NotARealPassword123!"},
    )

    assert login_response.status_code == 401


def test_owner_and_tenant_portals_open_without_credentials():
    db = SessionLocal()
    try:
        existing_portals = {
            user.username
            for user in db.query(User).filter(User.username.in_(["portal_owner", "portal_tenant"])).all()
        }
    finally:
        db.close()

    for role in ("OWNER", "TENANT"):
        response = client.get("/api/v1/pgs", headers={"X-Portal-Role": role})
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)

    db = SessionLocal()
    try:
        created_portals = db.query(User).filter(
            User.username.in_(["portal_owner", "portal_tenant"])
        ).all()
        for portal_user in created_portals:
            if portal_user.username not in existing_portals:
                db.delete(portal_user)
        db.commit()
    finally:
        db.close()
