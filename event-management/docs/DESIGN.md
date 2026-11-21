# Technical Design
## Corporate Event Management API

**Status:** Implemented baseline design (reviewed against source code, 18 November 2026).

---

## 1. Design principles

1. **Correctness first:** enforce business rules in the service layer and database.
2. **Clear contracts:** use Pydantic schemas for request and response bodies.
3. **Predictable errors:** return appropriate HTTP status codes and useful messages.
4. **Separation of concerns:** routers handle HTTP; services handle business rules; models represent persisted data.
5. **Secure configuration:** secrets are environment variables, never committed.
6. **Testability:** core rules must be covered by automated tests.
7. **Assignment alignment:** complete mandatory rubric requirements before optional extensions.

## 2. Implemented API contract

The following routes are implemented in the current application. The profile and current-user-registration endpoints support the browser frontend.

| Method | Endpoint | Expected success |
|---|---|---|
| POST | `/api/v1/events` | `201 Created` |
| GET | `/api/v1/events` | `200 OK` |
| GET | `/api/v1/events/{event_id}` | `200 OK` |
| PUT/PATCH | `/api/v1/events/{event_id}` | `200 OK` |
| DELETE | `/api/v1/events/{event_id}` | `204 No Content` |
| POST | `/api/v1/events/{event_id}/registrations` | `201 Created` |
| DELETE | `/api/v1/registrations/{registration_id}` | `200 OK` or `204 No Content`, chosen consistently |

Implemented: `PATCH` performs partial updates; `DELETE` returns 204 for a successful event deletion.

## 3. Data contracts

### Event creation
Implemented fields:
- `title`: non-empty string;
- `description`: optional string;
- `start_at`: date/time value;
- `location`: string if required by the assignment;
- `capacity`: positive integer.

### Event update
Use an update schema that matches the chosen HTTP method. Validate capacity and date/time consistently with creation.

### Employee registration
Implemented fields:
- `employee_name`;
- `employee_email`.

Employee accounts are created separately by an organization administrator. Registration uses the authenticated employee identity from the JWT; no employee name/email is accepted in the registration request.

### Response schemas
Return stable identifiers and the relevant event/registration fields. Do not return database credentials, internal tokens, or unnecessary internal metadata.

## 4. Business rules

### BR-01 — Event must exist
A registration can only be created for an existing event.

### BR-02 — Capacity must be positive
An event must not be created or updated with zero or negative capacity.

### BR-03 — Capacity cannot be exceeded
The number of active registrations must never exceed event capacity.

### BR-04 — No duplicate active registration
An employee cannot have two active registrations for the same event.

### BR-05 — Cancellation
Only an existing registration can be cancelled. Implemented: cancellation changes the registration status to `cancelled` and records `cancelled_at`. A cancelled registration can be reactivated if capacity is available.

### BR-06 — Missing resources
Operations on an unknown event or registration ID must return a not-found response.

### BR-07 — Update semantics
Updating an event must not silently create a new event when the ID does not exist.

### BR-08 — Event deletion
Implemented: deleting an event with any registration history is rejected with HTTP 409. Events without registrations can be deleted with HTTP 204.

## 5. HTTP status code policy

| Status | Use |
|---|---|
| `200 OK` | Successful retrieval or update; cancellation if returning a body |
| `201 Created` | Event or registration created |
| `204 No Content` | Successful deletion with no response body |
| `400 Bad Request` | A domain-level request conflict where appropriate |
| `404 Not Found` | Event or registration does not exist |
| `409 Conflict` | Duplicate registration or event capacity conflict |
| `422 Unprocessable Entity` | Request body or parameter fails schema validation |
| `500 Internal Server Error` | Unexpected server error; do not expose stack traces or secrets |

Use a consistent error response structure. FastAPI's default validation response may be retained or customized, but document whichever behavior is implemented. Do not return `200` for failed operations.

## 6. Database design considerations

- Use integer or UUID primary keys consistently.
- Use foreign keys for registration relationships.
- Add a uniqueness rule for employee/event registration.
- Store date/time consistently; prefer timezone-aware timestamps for real-world events.
- Store registration creation time.
- Decide whether registration status is required.
- Use transactions for registration creation and capacity checks.
- Keep database schema changes under a migration tool if Alembic is included.

## 7. Validation and error handling

Validation should occur at two levels:
1. Pydantic validates request shape and field constraints.
2. Service/database rules validate domain conditions and relational integrity.

Examples:
- missing title → validation error;
- capacity `0` → validation error;
- unknown event ID → not found;
- duplicate active registration → conflict;
- full event → conflict;
- unknown registration ID during cancellation → not found.

Unexpected exceptions should be logged server-side without returning sensitive details to the client.

## 8. Optional bonus design

### Pagination
Add `skip`/`limit` or `page`/`page_size` to event listing. Validate bounds and return a documented response shape. Avoid unbounded list responses.

### Search and filtering
Only implement filters that have clear product value and are testable, such as title search or date range. Document supported query parameters.

### JWT authentication
Implemented:
- passwords are hashed with Argon2; plaintext passwords are not stored;
- JWTs are signed using an environment-configured secret;
- tokens include expiry, issuer, and audience claims;
- protected endpoints validate the token and active user;
- administrator and employee permissions are enforced by dependencies and service queries.

### Async database operations
Not implemented. The application uses synchronous SQLAlchemy sessions and regular `def` route handlers. Do not describe the current implementation as asynchronous.

### Pytest
Test normal and failure paths. Keep tests deterministic and independent of production data.

## 9. Security baseline

- Keep `.env` out of Git.
- Use `.env.example` with placeholders.
- Validate all client input.
- Use parameterized ORM operations; do not construct SQL from untrusted strings.
- Do not expose stack traces, secrets, or raw database errors.
- Apply authentication/authorization if the final scope includes protected client operations.
- Do not claim multi-tenant privacy unless every relevant query is scoped and tested by tenant.


### Organization-scoped authorization

The API derives organization access from the authenticated user's validated JWT context.

Authorization rules:

| Operation | Organization Admin | Employee |
|---|---|---|
| List organization events | Allowed | Allowed |
| Retrieve organization event | Allowed | Allowed |
| Create event | Allowed | Denied |
| Update event | Allowed | Denied |
| Delete event | Allowed | Denied |
| Create employee account | Allowed | Denied |
| Register for organization event | Allowed by current endpoint | Allowed |
| Cancel own registration | Allowed | Allowed |
| Cancel another employee's registration | Allowed within own organization | Denied |
| List event registrations | Allowed within own organization | Denied |

Organization filters are enforced through application-level service queries.

This authorization model requires comprehensive cross-organization tests. Database-level isolation and production-grade tenant security remain separate verification requirements.


## 10. Operational design

- Local development: VS Code + WSL.
- Local API: Uvicorn.
- Database: PostgreSQL; hosted Supabase was discussed as a free-tier option.
- Repository: Git/GitHub.
- API testing: Swagger UI and Postman.
- Automated testing: Pytest.
- Hosting: Render was discussed as a possible free-tier host; Vercel is an alternative requiring serverless/database connection verification.

Free tiers can have limits, sleeping behavior, quotas, and changing terms. They are suitable for development/demo only unless their current terms meet the actual service requirements.

## 11. Definition of done

A feature is done only when:
- its endpoint works;
- request/response schemas are defined;
- business rules are enforced;
- correct status codes are returned;
- relevant tests pass;
- Swagger reflects the behavior;
- README/documentation is updated.
