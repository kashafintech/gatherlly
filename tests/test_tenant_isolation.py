
def _create_admin(client, organization_name, email, password):
    """Create an organization administrator and log in."""

    registration = client.post(
        "/api/v1/auth/register-organization",
        json={
            "organization_name": organization_name,
            "full_name": "Test Administrator",
            "email": email,
            "password": password,
        },
    )

    assert registration.status_code == 201, registration.text

    user = registration.json()

    login = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": user["organization_id"],
            "email": email,
            "password": password,
        },
    )

    assert login.status_code == 200, login.text

    return {
        "user": user,
        "token": login.json()["access_token"],
    }


def _create_employee(client, admin, full_name, email, password):
    """Create an employee under an administrator and log in."""

    admin_headers = {
        "Authorization": f"Bearer {admin['token']}"
    }

    creation = client.post(
        "/api/v1/auth/employees",
        headers=admin_headers,
        json={
            "full_name": full_name,
            "email": email,
            "password": password,
        },
    )

    assert creation.status_code == 201, creation.text

    user = creation.json()

    login = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": user["organization_id"],
            "email": email,
            "password": password,
        },
    )

    assert login.status_code == 200, login.text

    return {
        "user": user,
        "token": login.json()["access_token"],
    }


def test_same_email_can_login_to_different_organizations(
    client, event_payload
):
    """The organization ID must identify the correct account."""

    shared_email = "shared@example.com"

    admin_a = _create_admin(
        client,
        "Organization Alpha",
        shared_email,
        "AlphaPassword!2026",
    )

    admin_b = _create_admin(
        client,
        "Organization Beta",
        shared_email,
        "BetaPassword!2026",
    )

    assert (
        admin_a["user"]["organization_id"]
        != admin_b["user"]["organization_id"]
    )

    headers_a = {
        "Authorization": f"Bearer {admin_a['token']}"
    }

    headers_b = {
        "Authorization": f"Bearer {admin_b['token']}"
    }

    event_a_response = client.post(
        "/api/v1/events",
        headers=headers_a,
        json=event_payload,
    )
    assert event_a_response.status_code == 201, event_a_response.text
    event_a_id = event_a_response.json()["id"]

    event_b_payload = {
        **event_payload,
        "title": "Organization Beta Conference",
    }

    event_b_response = client.post(
        "/api/v1/events",
        headers=headers_b,
        json=event_b_payload,
    )
    assert event_b_response.status_code == 201, event_b_response.text
    event_b_id = event_b_response.json()["id"]

    # Organization Alpha can access its own event.
    assert client.get(
        f"/api/v1/events/{event_a_id}",
        headers=headers_a,
    ).status_code == 200

    # Organization Beta can access its own event.
    assert client.get(
        f"/api/v1/events/{event_b_id}",
        headers=headers_b,
    ).status_code == 200

    # Organization Alpha cannot access Organization Beta's event.
    assert client.get(
        f"/api/v1/events/{event_b_id}",
        headers=headers_a,
    ).status_code == 404

    # Organization Beta cannot access Organization Alpha's event.
    assert client.get(
        f"/api/v1/events/{event_a_id}",
        headers=headers_b,
    ).status_code == 404

    # Correct email and organization ID, but wrong password.
    wrong_login = client.post(
        "/api/v1/auth/login",
        json={
            "organization_id": admin_b["user"]["organization_id"],
            "email": shared_email,
            "password": "AlphaPassword!2026",
        },
    )

    assert wrong_login.status_code == 401


def test_admin_cannot_read_modify_delete_or_list_other_org_data(
    client, event_payload
):
    """An administrator cannot access another organization's resources."""

    admin_a = _create_admin(
        client,
        "Organization Alpha",
        "admin-a@example.com",
        "AdminAlphaPassword!2026",
    )

    admin_b = _create_admin(
        client,
        "Organization Beta",
        "admin-b@example.com",
        "AdminBetaPassword!2026",
    )

    headers_a = {
        "Authorization": f"Bearer {admin_a['token']}"
    }

    headers_b = {
        "Authorization": f"Bearer {admin_b['token']}"
    }

    created = client.post(
        "/api/v1/events",
        headers=headers_a,
        json=event_payload,
    )

    assert created.status_code == 201, created.text

    event_id = created.json()["id"]

    # Organization B's event listing must not contain Organization A's event.
    listing = client.get(
        "/api/v1/events",
        headers=headers_b,
    )

    assert listing.status_code == 200

    event_ids = {
        item["id"] for item in listing.json()["items"]
    }

    assert event_id not in event_ids

    # Another organization's event must not be readable.
    read = client.get(
        f"/api/v1/events/{event_id}",
        headers=headers_b,
    )
    assert read.status_code == 404

    # Another organization's event must not be modifiable.
    update = client.patch(
        f"/api/v1/events/{event_id}",
        headers=headers_b,
        json={"title": "Unauthorized Modification"},
    )
    assert update.status_code == 404

    # Another organization's event must not be deletable.
    delete = client.delete(
        f"/api/v1/events/{event_id}",
        headers=headers_b,
    )
    assert delete.status_code == 404

    # Another organization's registrations must not be accessible.
    registrations = client.get(
        f"/api/v1/events/{event_id}/registrations",
        headers=headers_b,
    )
    assert registrations.status_code == 404

    # Verify that Organization A's event still exists.
    owner_check = client.get(
        f"/api/v1/events/{event_id}",
        headers=headers_a,
    )
    assert owner_check.status_code == 200


def test_employees_cannot_access_other_org_events_or_cancel_other_users(
    client, event_payload
):
    """Check cross-organization access and registration ownership."""

    admin_a = _create_admin(
        client,
        "Organization Alpha",
        "alpha-admin@example.com",
        "AlphaAdminPassword!2026",
    )

    admin_b = _create_admin(
        client,
        "Organization Beta",
        "beta-admin@example.com",
        "BetaAdminPassword!2026",
    )

    employee_a1 = _create_employee(
        client,
        admin_a,
        "Employee A1",
        "employee-a1@example.com",
        "EmployeeA1Password!2026",
    )

    employee_a2 = _create_employee(
        client,
        admin_a,
        "Employee A2",
        "employee-a2@example.com",
        "EmployeeA2Password!2026",
    )

    employee_b = _create_employee(
        client,
        admin_b,
        "Employee B",
        "employee-b@example.com",
        "EmployeeBPassword!2026",
    )

    admin_a_headers = {
        "Authorization": f"Bearer {admin_a['token']}"
    }

    admin_b_headers = {
        "Authorization": f"Bearer {admin_b['token']}"
    }

    employee_a1_headers = {
        "Authorization": f"Bearer {employee_a1['token']}"
    }

    employee_a2_headers = {
        "Authorization": f"Bearer {employee_a2['token']}"
    }

    employee_b_headers = {
        "Authorization": f"Bearer {employee_b['token']}"
    }

    created = client.post(
        "/api/v1/events",
        headers=admin_a_headers,
        json=event_payload,
    )

    assert created.status_code == 201, created.text

    event_id = created.json()["id"]

    # Employee A1 registers for Organization A's event.
    registration = client.post(
        f"/api/v1/events/{event_id}/registrations",
        headers=employee_a1_headers,
    )

    assert registration.status_code == 201, registration.text

    registration_id = registration.json()["id"]

    # Employee B cannot read Organization A's event.
    read = client.get(
        f"/api/v1/events/{event_id}",
        headers=employee_b_headers,
    )
    assert read.status_code == 404

    # Employee B cannot register for Organization A's event.
    cross_org_registration = client.post(
        f"/api/v1/events/{event_id}/registrations",
        headers=employee_b_headers,
    )
    assert cross_org_registration.status_code == 404

    # Employee A2 cannot cancel Employee A1's registration.
    other_employee_cancel = client.delete(
        f"/api/v1/registrations/{registration_id}",
        headers=employee_a2_headers,
    )
    assert other_employee_cancel.status_code == 404

    # Employee B cannot cancel Organization A's registration.
    cross_org_cancel = client.delete(
        f"/api/v1/registrations/{registration_id}",
        headers=employee_b_headers,
    )
    assert cross_org_cancel.status_code == 404

    # Organization B's administrator cannot cancel it either.
    admin_cross_org_cancel = client.delete(
        f"/api/v1/registrations/{registration_id}",
        headers=admin_b_headers,
    )
    assert admin_cross_org_cancel.status_code == 404

    # The original owner can still cancel their own registration.
    owner_cancel = client.delete(
        f"/api/v1/registrations/{registration_id}",
        headers=employee_a1_headers,
    )
    assert owner_cancel.status_code == 200
    assert owner_cancel.json()["status"] == "cancelled"
