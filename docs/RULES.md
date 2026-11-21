# Project Rules and Engineering Standards
## Corporate Event Management API

These rules apply to implementation, testing, documentation, and AI-assisted changes.

---

## 1. Requirement priority

1. Follow the official IEC assignment brief and rubric.
2. Complete all mandatory requirements before optional features.
3. Use the decisions in `PRD.md`, `ARCHITECTURE.md`, and `DESIGN.md`.
4. Treat undecided items as open decisions, not facts.
5. Do not add scope that risks the mandatory submission.

## 2. Architecture rules

- Keep the required modules identifiable: `main.py`, `db.py`, `models.py`, `schemas.py`, and `services.py`.
- Keep event routes in `routers/events.py`.
- Keep registration routes in `routers/registrations.py`.
- Route handlers must remain thin.
- Business rules belong in `services.py`.
- SQLAlchemy persistence definitions belong in `models.py`.
- Pydantic request/response contracts belong in `schemas.py`.
- Database engine/session/dependency setup belongs in `db.py`.
- Do not duplicate business rules across routes.

## 3. Python code standards

- Use clear, descriptive names.
- Follow PEP 8 conventions.
- Use type hints for public functions and important data structures.
- Keep functions focused and reasonably small.
- Avoid unnecessary global mutable state.
- Remove unused imports and debug prints before submission.
- Do not swallow exceptions silently.
- Add comments when they explain why, not merely what a line does.

## 4. API rules

- Use consistent route naming and HTTP methods.
- Use Pydantic models for request and response validation.
- Set explicit response models and status codes.
- Return `201 Created` for successful resource creation.
- Return `404 Not Found` for missing resources.
- Return `409 Conflict` for duplicate registration or capacity conflicts, where appropriate.
- Return `422 Unprocessable Entity` for schema validation failures.
- Do not return success status codes for failed operations.
- Document expected errors in OpenAPI/Swagger.
- Keep error messages useful but do not disclose stack traces or secrets.

## 5. Business-rule rules

- A registration must reference an existing event.
- An employee must not have duplicate active registrations for one event.
- Registration must not exceed event capacity.
- Capacity must be checked safely when concurrent requests are possible.
- Cancellation must apply only to a valid existing registration.
- Event deletion behavior with existing registrations must be deliberate and tested.
- Do not rely only on frontend/client validation; enforce rules in the backend and database where practical.

## 6. Database rules

- Use primary keys and foreign keys.
- Add database constraints for important invariants where practical.
- Use SQLAlchemy rather than building SQL strings from untrusted input.
- Use transactions for multi-step writes.
- Keep schema changes reproducible; use Alembic if included.
- Never use production data in automated tests.
- Never commit real database credentials.

## 7. Security and configuration rules

- Store secrets in environment variables.
- Commit `.env.example` with placeholder values only.
- Add `.env` and other secret files to `.gitignore`.
- Never paste API keys, passwords, JWT secrets, or full production database URLs into source files, README examples, screenshots, or public issues.
- If JWT is implemented, hash passwords and validate token expiry/signature.
- Do not claim tenant isolation unless it is implemented and tested for every relevant query.

## 8. Git and GitHub rules

- Make small, meaningful commits.
- Use commit messages that describe the change, for example:
  - `feat: add event CRUD endpoints`
  - `feat: enforce registration capacity`
  - `test: cover duplicate registration`
  - `docs: add API setup instructions`
- Do not commit virtual environments, caches, local databases, `.env`, or generated secrets.
- Keep `requirements.txt` updated.
- Push only code that has been checked for secrets.
- Do not claim a GitHub push or deployment succeeded unless it was actually verified.

## 9. Testing rules

At minimum, test:
- create event with valid data;
- reject invalid event data;
- list events;
- retrieve existing event;
- return 404 for missing event;
- update existing event;
- delete existing event;
- register employee successfully;
- reject registration for missing event;
- reject duplicate active registration;
- reject registration when event is full;
- cancel an existing registration;
- return 404 when cancelling an unknown registration.

For each bug fix, add or update a test where practical. Report the actual test command and result; never fabricate a passing result.

## 10. Documentation and submission rules

- README must explain setup, environment variables, database setup, run commands, tests, and API documentation URL/path.
- Keep `requirements.txt` aligned with the actual imports and environment.
- Include Swagger screenshots that come from the running application.
- Include AI usage documentation that truthfully describes how AI assistance was used and what the student reviewed/changed.
- Include a real demo recording showing the implemented API.
- Do not include fake screenshots, fake logs, placeholder deployment URLs presented as live, or unimplemented feature claims.

## 11. AI-assisted development rules

- AI-generated code must be reviewed and understood before submission.
- Run the code and tests after applying generated changes.
- Never invent test results, references, or implementation status.
- Keep this project’s files consistent with the actual codebase.
- If the assignment has a rule about disclosure of AI assistance, follow that rule exactly.

## 12. Definition of complete

A task is complete only when:
1. the implementation exists;
2. it runs in the target environment;
3. relevant tests pass;
4. expected errors and edge cases are handled;
5. documentation matches the implementation;
6. no secrets are exposed;
7. the change is committed to Git when appropriate.
