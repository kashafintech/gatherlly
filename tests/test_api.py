
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_event_crud(client, auth_headers, event_payload):
    created = client.post(
        "/api/v1/events",
        headers=auth_headers,
        json=event_payload,
    )
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]

    fetched = client.get(
        f"/api/v1/events/{event_id}",
        headers=auth_headers,
    )
    assert fetched.status_code == 200
    assert fetched.json()["title"] == event_payload["title"]

    updated = client.patch(
        f"/api/v1/events/{event_id}",
        headers=auth_headers,
        json={"title": "Updated Technology Conference"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated Technology Conference"

    deleted = client.delete(
        f"/api/v1/events/{event_id}",
        headers=auth_headers,
    )
    assert deleted.status_code == 204


def test_auth_required_for_private_endpoints(client):
    response = client.get("/api/v1/events")
    assert response.status_code == 401


def test_employee_registration_and_duplicate_prevention(
    client, auth_headers, employee, event_payload
):
    event_response = client.post(
        "/api/v1/events",
        headers=auth_headers,
        json=event_payload,
    )
    assert event_response.status_code == 201, event_response.text

    event = event_response.json()

    employee_headers = {
        "Authorization": f"Bearer {employee['token']}"
    }

    path = f"/api/v1/events/{event['id']}/registrations"

    first = client.post(path, headers=employee_headers)
    assert first.status_code == 201, first.text

    duplicate = client.post(path, headers=employee_headers)
    assert duplicate.status_code == 409


def test_capacity_is_enforced(client, auth_headers, employee, event_payload):
    event_payload["capacity"] = 1

    event_response = client.post(
        "/api/v1/events",
        headers=auth_headers,
        json=event_payload,
    )
    assert event_response.status_code == 201, event_response.text

    event = event_response.json()

    employee_headers = {
        "Authorization": f"Bearer {employee['token']}"
    }

    path = f"/api/v1/events/{event['id']}/registrations"

    first = client.post(path, headers=employee_headers)
    assert first.status_code == 201, first.text

    # Create a second employee in the same organization.
    second = client.post(
        "/api/v1/auth/employees",
        headers=auth_headers,
        json={
            "full_name": "Employee Two",
            "email": "employee-two@example.com",
            "password": "EmployeeTwoPassword!2026",
        },
    )

    assert second.status_code == 201, second.text

    # Login using the employee's organization ID.
    login = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": second.json()["organization_id"],
            "email": "employee-two@example.com",
            "password": "EmployeeTwoPassword!2026",
        },
    )

    assert login.status_code == 200, login.text

    second_headers = {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }

    full = client.post(path, headers=second_headers)
    assert full.status_code == 409


def test_admin_cannot_access_another_organization_event(
    client, organization_admin, event_payload
):
    # Organization A admin creates an event.
    first_headers = {
        "Authorization": f"Bearer {organization_admin['token']}"
    }

    event_response = client.post(
        "/api/v1/events",
        headers=first_headers,
        json=event_payload,
    )

    assert event_response.status_code == 201, event_response.text

    event = event_response.json()

    # Register a second organization.
    second_org = client.post(
        "/api/v1/auth/register-organization",
        json={
            "organization_name": "Different Corporation",
            "full_name": "Other Admin",
            "email": "other-admin@example.com",
            "password": "OtherAdminPassword!2026",
        },
    )

    assert second_org.status_code == 201, second_org.text

    # Login using Organization B's ID.
    login = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": second_org.json()["organization_id"],
            "email": "other-admin@example.com",
            "password": "OtherAdminPassword!2026",
        },
    )

    assert login.status_code == 200, login.text

    other_headers = {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }

    # Organization B admin must not access Organization A's event.
    response = client.get(
        f"/api/v1/events/{event['id']}",
        headers=other_headers,
    )

    assert response.status_code == 404


def test_invalid_event_capacity_is_rejected(client, auth_headers, event_payload):
    event_payload["capacity"] = 0
    response = client.post("/api/v1/events", headers=auth_headers, json=event_payload)
    assert response.status_code == 422


def test_registration_for_missing_event_returns_404(client, employee):
    headers = {"Authorization": f"Bearer {employee['token']}"}
    response = client.post(
        "/api/v1/events/00000000-0000-0000-0000-000000000000/registrations",
        headers=headers,
    )
    assert response.status_code == 404


def test_event_with_registration_history_cannot_be_deleted(
    client, auth_headers, employee, event_payload
):
    created = client.post("/api/v1/events", headers=auth_headers, json=event_payload)
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]

    employee_headers = {"Authorization": f"Bearer {employee['token']}"}
    registration = client.post(
        f"/api/v1/events/{event_id}/registrations",
        headers=employee_headers,
    )
    assert registration.status_code == 201, registration.text

    deleted = client.delete(f"/api/v1/events/{event_id}", headers=auth_headers)
    assert deleted.status_code == 409


def test_repeated_cancellation_returns_conflict(
    client, auth_headers, employee, event_payload
):
    created = client.post("/api/v1/events", headers=auth_headers, json=event_payload)
    assert created.status_code == 201, created.text
    event_id = created.json()["id"]
    employee_headers = {"Authorization": f"Bearer {employee['token']}"}

    registration = client.post(
        f"/api/v1/events/{event_id}/registrations",
        headers=employee_headers,
    )
    assert registration.status_code == 201, registration.text
    registration_id = registration.json()["id"]

    first = client.delete(
        f"/api/v1/registrations/{registration_id}",
        headers=employee_headers,
    )
    assert first.status_code == 200
    assert first.json()["status"] == "cancelled"

    second = client.delete(
        f"/api/v1/registrations/{registration_id}",
        headers=employee_headers,
    )
    assert second.status_code == 409


def test_employee_profile_and_my_registrations(client, employee):
    headers = {"Authorization": f"Bearer {employee['token']}"}
    profile = client.get("/api/v1/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["role"] == "employee"
    assert profile.json()["organization_name"] == "Example Corporation"

    registrations = client.get("/api/v1/registrations/mine", headers=headers)
    assert registrations.status_code == 200
    assert registrations.json() == []


def test_frontend_and_static_assets_are_served(client):
    assert client.get("/").status_code == 200
    assert "text/html" in client.get("/").headers["content-type"]
    assert client.get("/style.css").status_code == 200
    assert client.get("/script.js").status_code == 200
    assert client.get("/assets/logo.svg").status_code == 200
