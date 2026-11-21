# API Examples

Base URL for local development: `http://127.0.0.1:8000`

All request bodies below are illustrative and must match the live OpenAPI schema.

## 1. Register an organization administrator

`POST /api/v1/auth/register-organization`

```json
{
  "organization_name": "Example Corporation",
  "full_name": "Alex Morgan",
  "email": "admin@example.com",
  "password": "ReplaceWithAUniqueStrongPassword!"
}
```

## 2. Login

`POST /api/v1/auth/login`

```json
{
  "organization_id": "00000000-0000-0000-0000-000000000000",
  "email": "admin@example.com",
  "password": "ReplaceWithAUniqueStrongPassword!"
}
```

Use the returned `access_token` as a Bearer token for protected endpoints.

## 3. Create an employee

`POST /api/v1/auth/employees`

Header: `Authorization: Bearer <ACCESS_TOKEN>`

```json
{
  "full_name": "Jordan Lee",
  "email": "jordan@example.com",
  "password": "ReplaceWithAnotherStrongPassword!"
}
```

## 4. Create an event

`POST /api/v1/events`

```json
{
  "title": "Annual Technology Conference",
  "description": "Company technology conference",
  "starts_at": "2027-05-20T09:00:00Z",
  "location": "New York, NY",
  "capacity": 100
}
```

## 5. List events

`GET /api/v1/events?limit=20&offset=0&search=technology`

## 6. Register an employee

`POST /api/v1/events/{event_id}/registrations`

No request body is required. The employee identity comes from the bearer token.

## 7. Cancel a registration

`DELETE /api/v1/registrations/{registration_id}`

An employee can cancel their own registration. An administrator can cancel a registration within their own organization.

## Expected error examples

- `401`: missing, invalid, or expired authentication.
- `403`: authenticated user lacks the required role.
- `404`: resource not found within the authenticated organization.
- `409`: duplicate registration, full event, or event with registration history cannot be deleted.
- `422`: invalid request data.

Use Swagger UI at `/docs` for the authoritative request and response schemas.


## 8. Get the authenticated profile

`GET /api/v1/auth/me`

Header: `Authorization: Bearer <ACCESS_TOKEN>`

Returns the authenticated user's profile and organization name. This endpoint is used by the browser frontend.

## 9. List the authenticated employee's registrations

`GET /api/v1/registrations/mine`

Header: `Authorization: Bearer <ACCESS_TOKEN>`

Returns registrations owned by the authenticated employee, including event title, date/time, and location. The endpoint is available to authenticated users; results are scoped to the current user and organization.
