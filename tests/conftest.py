import os
import uuid

# Configure test settings before importing application modules.
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "test-only-secret-key-that-is-long-enough-123456789"
os.environ["AUTO_CREATE_TABLES"] = "true"
os.environ["CORS_ORIGINS"] = "http://testserver"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def organization_admin(client):
    response = client.post(
        "/api/v1/auth/register-organization",
        json={
            "organization_name": "Example Corporation",
            "full_name": "Admin User",
            "email": f"admin-{uuid.uuid4().hex[:8]}@example.com",
            "password": "StrongTestPassword!2026",
        },
    )
    assert response.status_code == 201, response.text
    user = response.json()
    login = client.post(
        "/api/v1/auth/login",
        
json={
    "organization_id": user["organization_id"],
    "email": user["email"],
    "password": "StrongTestPassword!2026",
},

    )
    assert login.status_code == 200, login.text
    return {"user": user, "token": login.json()["access_token"]}


@pytest.fixture()
def employee(client, organization_admin):
    headers = {"Authorization": f"Bearer {organization_admin['token']}"}
    response = client.post(
        "/api/v1/auth/employees",
        headers=headers,
        json={
            "full_name": "Employee One",
            "email": f"employee-{uuid.uuid4().hex[:8]}@example.com",
            "password": "EmployeePassword!2026",
        },
    )
    assert response.status_code == 201, response.text
    user = response.json()
    login = client.post(
        "/api/v1/auth/login",
        
json={
    "organization_id": user["organization_id"],
    "email": user["email"],
    "password": "EmployeePassword!2026",
},

    )
    assert login.status_code == 200, login.text
    return {"user": user, "token": login.json()["access_token"]}


@pytest.fixture()
def auth_headers(organization_admin):
    return {"Authorization": f"Bearer {organization_admin['token']}"}


@pytest.fixture()
def event_payload():
    return {
        "title": "Annual Technology Conference",
        "description": "Internal corporate technology event",
        "starts_at": "2027-05-20T09:00:00Z",
        "location": "New York, NY",
        "capacity": 2,
    }
