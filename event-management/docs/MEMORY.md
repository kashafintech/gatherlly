# Project Memory
## Corporate Event Management API

This file is a concise, durable context file for contributors and AI coding assistants. It records confirmed project direction and warns against treating undecided items as facts.

---

## 1. Project identity

- Project: **Corporate Event Management API**
- Context: IEC assignment, designed with a real client-facing backend mindset.
- Primary objective: complete all mandatory assignment requirements and target an A+ result.
- Assignment deadline stated in prior discussion: **18 November 2026**.
- The API manages corporate events and employee registrations.

## 2. User's working environment

- Editor: Visual Studio Code.
- Terminal/environment: WSL.
- Python is installed, but the exact version was not confirmed in the discussion.
- PostgreSQL was not installed at the time of the environment check.
- Git installation/status was not confirmed.
- The previously referenced Bookstore API source code was not available.

Do not assume the environment has since changed. Verify versions and installed tools before giving installation commands.

## 3. Confirmed core requirements

- Event CRUD.
- Employee registration and cancellation.
- Prevent duplicate registrations.
- Enforce event capacity.
- Reject registration for a non-existent event.
- Pydantic validation.
- Appropriate HTTP errors/status codes.
- OpenAPI/Swagger documentation.
- Required layered project structure including `db.py`, `models.py`, `schemas.py`, `services.py`, and `main.py`.
- Git/GitHub repository.
- `requirements.txt` and README.
- Swagger screenshots and AI usage documentation.
- Project demo video.

The assignment rubric was discussed as 100 mandatory points plus 20 optional bonus points, with final score capped at 100. The point allocation should be checked against the original assignment/rubric before being repeated as authoritative.

## 4. Bonus features discussed

- Pagination.
- Search/filtering.
- JWT authentication.
- Async database operations.
- Pytest.

Implement core requirements first. A feature must not be marked complete until it exists in code and has evidence/tests.

## 5. Technology direction discussed

Preferred zero-budget development direction:
- Python + FastAPI.
- PostgreSQL.
- SQLAlchemy.
- Pydantic.
- Git + GitHub.
- Swagger UI and Postman.
- Pytest.
- Supabase was discussed as a hosted PostgreSQL option.
- Render was discussed as a possible FastAPI hosting option.
- Vercel was also discussed, but its serverless behavior and database connection approach need verification.

The exact hosting provider and sync/async database approach were not finalized. Keep local development independent of a hosting provider.

## 6. Product direction

The user wants the project to be built as if providing a backend service to a US-based client, rather than as a bare classroom CRUD exercise.

This is a product-quality direction, not permission to invent additional mandatory requirements.

The current implementation already includes organization-scoped accounts and application-layer data filtering.

Each organization has its own users and events. Authentication tokens carry organization context, and application queries use that context to scope access.

However, production-grade tenant isolation is not yet verified. Do not claim complete multi-tenant security until authentication ambiguity, database-level protections, and cross-organization security tests have been addressed.


## 7. Explicitly out of confirmed scope

- Groq/AI functionality.
- A frontend application.
- Payment processing.
- Email/SMS integrations.
- Production-grade tenant isolation and independently verified database-level security.
- Always-on production hosting.

These may be future enhancements only if the user requests them or the assignment brief requires them.

## 8. Working rules for future contributors / AI assistants

1. Read `PRD.md`, `ARCHITECTURE.md`, `DESIGN.md`, and `RULES.md` before changing the project.
2. Preserve the assignment's mandatory requirements.
3. Do not invent requirements, completed features, test results, deployment URLs, credentials, or screenshots.
4. Clearly label proposed decisions until implemented and verified.
5. Keep business logic in `services.py`.
6. Keep route handlers thin.
7. Do not hard-code secrets or commit `.env`.
8. Do not claim production-grade tenant isolation based only on application-level organization filters. Verify every relevant access path and security boundary.
9. Update documentation when the actual implementation changes.
10. Report what was tested and what remains unverified.

## 9. Remaining verification and environment checks

- Project runtime target is Python 3.12; local developer environment still needs verification.
- Confirm whether Git is installed.
- Confirm final event fields and employee identity model from the assignment brief.
- Cancellation is implemented as a status change to `cancelled` with a timestamp; reactivation is supported.
- Event deletion is rejected with HTTP 409 when any registration history exists.
- Synchronous SQLAlchemy is implemented.
- Vercel configuration is included, but an actual hosted deployment still requires environment variables and verification.
- JWT authentication is implemented.
- Verify cross-organization security for all event and registration operations.
- Login requires organization_id + email + password to disambiguate identical emails across organizations.
- Decide whether database-level Row Level Security and additional tenant-integrity constraints are required before production use.


\n\n## 10. Frontend extension\n\nA responsive same-origin browser UI is included under `public/`, with event listing/creation/editing, organization registration/login, employee creation, and registration/cancellation views. It is a lightweight HTML/CSS/JavaScript frontend, not a separate React/Vue application.\n