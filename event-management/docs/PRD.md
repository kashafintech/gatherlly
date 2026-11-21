# Product Requirements Document (PRD)
## Corporate Event Management API

**Document status:** Project baseline  
**Project type:** IEC assignment with a client-facing service design  
**Target:** Complete all mandatory rubric requirements and implement suitable bonus features  
**Deadline stated in the assignment discussion:** 18 November 2026

---

## 1. Product overview

The Corporate Event Management API is a backend service that allows an organization to create and manage corporate events and employee registrations. It exposes documented HTTP endpoints that a company website, frontend application, or API client can use.

The project must satisfy the IEC assignment requirements while being structured and documented like a maintainable service that could later be extended for real organizational clients.

The original assignment baseline is an API/backend project. A lightweight responsive browser frontend was added as a requested project extension; it consumes the same FastAPI endpoints and does not replace backend validation or authorization.

## 2. Problem statement

Organizations need a consistent way to:
- create and maintain corporate event records;
- allow employees to register for events;
- cancel registrations;
- prevent duplicate registrations;
- prevent registrations from exceeding an event's capacity; and
- receive clear validation and error responses.

The API centralizes these operations and persists their data in a relational database.

## 3. Goals

1. Deliver every mandatory feature identified in the assignment rubric.
2. Keep HTTP route handlers thin and place business rules in a service layer.
3. validate incoming and outgoing data with Pydantic schemas.
4. Persist data in PostgreSQL through SQLAlchemy.
5. expose interactive OpenAPI/Swagger documentation.
6. Provide automated tests for core functionality and business rules.
7. Maintain a clear GitHub repository with setup instructions, screenshots, and a demo.
8. Keep the initial implementation within a zero-budget toolchain where free tiers are sufficient.


## 4. Non-goals and scope boundaries

The following are not part of the current confirmed release scope:
- a production-grade public website or enterprise frontend;
- AI/Groq features;
- payment processing, ticket sales, email/SMS notifications, or calendar integrations;
- production-grade enterprise identity management;
- production-grade multi-tenant isolation with independently verified database-level security;
- a guarantee of always-on hosting from a free deployment tier.

### Current organization-scoped implementation

The current application includes basic organization-scoped data access at the application layer and a responsive browser frontend for authentication, event management, and registration workflows.

Implemented behavior:
- Organization registration creates a new organization and its first administrator.
- Every user belongs to an organization through `organization_id`.
- Every event belongs to an organization through `organization_id`.
- Administrators create employees within their own organization.
- Events are created, listed, retrieved, updated, and deleted using the authenticated user's organization context.
- Registration creation is restricted to events belonging to the authenticated user's organization.
- Employees can cancel their own registrations.
- Administrators can manage registrations within their own organization.

These controls represent an implemented application-level organization-scoping baseline. They must not be described as fully verified or production-grade multi-tenant isolation.

Production-grade isolation still requires comprehensive cross-organization security tests, review of database-level protections, and resolution of the authentication identity ambiguity. 


## 5. Users and usage scenario

### Primary API consumer
A company or its internal application calls the API to manage corporate events and employee registrations.

### Example scenario
1. An authorized API consumer creates an event with a title, description, date/time, location, and capacity.
2. The consumer retrieves the event or lists available events.
3. An employee is registered for an existing event.
4. The API checks that the event exists, that the employee is not already registered, and that capacity is available.
5. The API stores the registration and returns a successful response.
6. The employee's registration can later be cancelled.
7. The consumer can retrieve event and registration information.


Authentication and authorization are implemented using JWT.

The authenticated user context includes:
- user ID;
- organization ID;
- user role.

Organization-scoped access is derived from the validated authentication context rather than trusting an organization ID supplied by the client.

Administrators manage events and employees within their own organization. Authenticated users can access events within their organization and perform registration operations according to their permissions.

## 6. Functional requirements

### FR-01 — Event creation
The API shall allow a valid event to be created.

Minimum data should include:
- event title;
- description (if included in the final schema);
- date/time;
- location (if included in the final schema);
- capacity.

The final field names and required/optional status must match the implemented Pydantic schema and assignment brief.

### FR-02 — Event retrieval
The API shall support:
- retrieving a single event by its identifier; and
- listing events.

### FR-03 — Event update
The API shall allow an existing event to be updated using validated input.

### FR-04 — Event deletion
The API shall allow an existing event to be deleted, with a defined response when the identifier does not exist. The effect of deletion on registrations must be explicitly implemented and tested (for example, database cascade or a controlled rejection); do not leave this behavior accidental.

### FR-05 — Employee registration
The API shall allow an employee to register for an existing event.

### FR-06 — Registration cancellation
The API shall allow an existing registration to be cancelled.

### FR-07 — Duplicate prevention
An employee must not have more than one active registration for the same event. Enforce this in application logic and, where practical, with a database uniqueness constraint.

### FR-08 — Event existence
A registration request for a non-existent event must be rejected with an appropriate HTTP error.

### FR-09 — Capacity enforcement
The API must reject a registration when the event has reached its configured capacity. Capacity checking must be designed to avoid overbooking under concurrent requests; a transaction/locking or equivalent safe strategy should be used if supported by the selected database implementation.

### FR-10 — Input validation
Pydantic schemas shall validate request data and produce clear validation responses for invalid input.

### FR-11 — HTTP error handling
The API shall use appropriate HTTP status codes and consistent error response behavior for success, validation failure, missing resources, conflicts, and unexpected server errors.

### FR-12 — API documentation


### FR-13 — Organization-scoped access

The API shall maintain organization-scoped data access.

Requirements:
- Each user must belong to an organization.
- Each event must belong to an organization.
- Users must only access events belonging to their organization.
- Administrators must only manage employees and events within their organization.
- Registration creation must verify that the target event belongs to the authenticated user's organization.
- Registration cancellation must enforce organization boundaries and employee ownership rules.

Verification:
Cross-organization access must be tested with multiple organizations, administrators, and employees. Application-level filters alone must not be treated as proof of production-grade tenant isolation.

FastAPI's OpenAPI schema and Swagger UI shall describe the available endpoints, request models, response models, and expected errors.

## 7. Quality and repository requirements

- Use the required layered structure: `main.py`, `db.py`, `models.py`, `schemas.py`, and `services.py`, with routers separated from the application entry point.
- Keep business logic in `services.py`; route handlers should coordinate input/output and call services.
- Use environment variables for configuration and secrets.
- Never commit `.env`, passwords, database URLs, tokens, or other secrets.
- Include `requirements.txt` with the dependencies needed to run the project.
- Include a useful `README.md`.
- Use Git and publish the source repository to GitHub.
- Include Swagger screenshots and documentation of AI assistance/usage as required by the rubric.
- Record a project demo video as required by the rubric.

## 8. Bonus features

The assignment discussion identified these bonus opportunities. They are optional relative to the mandatory scope:

| Bonus | Points stated in the discussed rubric | Acceptance evidence |
|---|---:|---|
| Pagination | 3 | List endpoint supports page/limit or equivalent and returns consistent metadata |
| Search/filtering | 3 | Event listing can filter by supported fields |
| JWT authentication | 5 | Token issuance/validation and protected routes are tested |
| Async database operations | 4 | Database access is genuinely asynchronous end-to-end |
| Pytest | 5 | Automated tests cover endpoints, validation, and business rules |

Do not claim a bonus is complete until code and test evidence exist. The rubric was discussed as 100 mandatory points plus 20 bonus points, with the final score capped at 100; verify the original assignment sheet before relying on this arithmetic.

## 9. Implemented API surface

The following endpoints are present in the current source code.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/auth/register-organization` | Create an organization and its first administrator |
| `POST` | `/api/v1/auth/login` | Authenticate with organization ID, email, and password |
| `GET` | `/api/v1/auth/me` | Return the authenticated user's profile |
| `POST` | `/api/v1/auth/employees` | Administrator creates an employee account |
| `POST` | `/api/v1/events` | Create event (administrator) |
| `GET` | `/api/v1/events` | List/search/paginate organization events |
| `GET` | `/api/v1/events/{event_id}` | Retrieve an organization event |
| `PATCH` | `/api/v1/events/{event_id}` | Partially update event (administrator) |
| `DELETE` | `/api/v1/events/{event_id}` | Delete event when it has no registration history |
| `POST` | `/api/v1/events/{event_id}/registrations` | Register authenticated user |
| `GET` | `/api/v1/events/{event_id}/registrations` | Administrator lists event registrations |
| `GET` | `/api/v1/registrations/mine` | List authenticated user's registrations |
| `DELETE` | `/api/v1/registrations/{registration_id}` | Cancel an owned registration or an org registration as admin |

## 10. Acceptance criteria

The project is ready for submission when:
- all mandatory endpoints work against a persistent database;
- event CRUD operations are tested;
- registration and cancellation work;
- duplicate registration is rejected;
- registration for a missing event is rejected;
- capacity cannot be exceeded;
- invalid payloads receive validation errors;
- missing resources and conflicts return appropriate status codes;
- Swagger UI accurately documents the API;
- the project follows the required layered architecture;
- `requirements.txt` and README allow another person to set up the project;
- the GitHub repository contains the source and required documentation;
- Swagger screenshots, AI-use documentation, and demo video are included as required.
- Organization-scoped event and registration access is verified using cross-organization positive and negative security tests.

## 11. Implemented decisions and remaining verification

- Event timestamps are stored using timezone-aware SQLAlchemy `DateTime(timezone=True)` columns.
- Employee accounts are created separately by an organization administrator; registration identity comes from the authenticated JWT.
- Cancellation changes status to `cancelled`, records `cancelled_at`, and allows reactivation when capacity permits.
- Event deletion is rejected with HTTP 409 when registration history exists.
- JWT authentication is implemented.
- Synchronous SQLAlchemy sessions are implemented; async database operations are not implemented.
- The repository includes a Vercel FastAPI entry point, but an actual deployment and hosted PostgreSQL connection have not been verified.
- Organization access is enforced at the application layer. Database-level Row Level Security and production-grade tenant isolation are not implemented.

The original assignment brief remains the authority for grading requirements. Verify its exact mandatory/bonus wording before submission.

## 12. Frontend extension (added 18 November 2026)

A responsive browser interface is included in `public/`:
- `index.html` provides the sign-in, organization registration, dashboard, event list, and dialogs.
- `style.css` provides responsive layout and styling.
- `script.js` calls the FastAPI endpoints for authentication, profile, event CRUD, employee creation, and registration workflows.
- `assets/logo.svg` is the local brand asset.

The frontend is a lightweight single-page interface, not a separate frontend framework or independently deployed service. It relies on the same API and database. Authentication tokens are held in browser `sessionStorage` and are cleared on sign-out/session expiry. The frontend must not be treated as a security boundary; backend authorization remains authoritative.
