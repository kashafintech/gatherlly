# Corporate Event Management System

A FastAPI + SQLAlchemy corporate event management application with a lightweight responsive HTML/CSS/JavaScript frontend. Organizations can create an administrator account, manage employees and events, and let employees register for or cancel event attendance.

## Features

- Organization registration and administrator account creation
- JWT login using organization ID, email, and password
- Password hashing
- Role-based access: organization administrators and employees
- Event create, list, retrieve, partial update, and delete
- Event search and pagination
- Employee account creation by an administrator
- Event registration, duplicate prevention, capacity enforcement, cancellation, and reactivation
- Application-level organization-scoped data access
- Responsive browser frontend
- FastAPI OpenAPI documentation and Swagger UI
- Pytest API and organization-access tests

## Technology

- Python 3.12
- FastAPI
- SQLAlchemy 2.x (synchronous sessions)
- Pydantic / pydantic-settings
- PostgreSQL with psycopg 3 (production)
- SQLite (local development/tests)
- JWT (PyJWT) and argon2-cffi password hashing
- HTML, CSS, and vanilla JavaScript
- Vercel Python function entry point

## Repository layout

```text
.
├── index.py                 # Vercel FastAPI entry point
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── dependencies.py
│   ├── services.py
│   └── routers/
├── docs/
│   ├── AI_USAGE.md
│   ├── DEMO_SCRIPT.md
│   └── screenshots/
├── migrations/
│   └── 001_initial.sql
├── public/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── assets/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── vercel.json
```

## Local setup

1. Install Python 3.12.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # macOS / Linux / WSL:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`. The default local configuration uses SQLite and automatically creates tables.
5. Start the API and frontend:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Open `http://127.0.0.1:8000`. Swagger UI is at `http://127.0.0.1:8000/docs`.

## First use

- Choose **Create organization** to create an organization and its first administrator.
- Save the returned Organization ID. It is required for sign-in.
- Sign in using the Organization ID, email, and password.
- Administrators can create events and employee accounts.
- Employees sign in using the organization ID and their own account credentials, then register for available events.
- An employee can cancel their own active registration.

## Environment variables

| Variable | Purpose |
|---|---|
| `APP_NAME` | Application display name |
| `APP_VERSION` | API version |
| `APP_ENV` | `development`, `test`, or `production` |
| `DATABASE_URL` | SQLAlchemy database URL |
| `JWT_SECRET` | JWT signing secret; use a unique random value in production |
| `JWT_ALGORITHM` | JWT signing algorithm (HS256 by default) |
| `ACCESS_TOKEN_MINUTES` | Token lifetime |
| `CORS_ORIGINS` | Comma-separated browser origins |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames, or `*` for development |
| `AUTO_CREATE_TABLES` | Local table creation; must be `false` in production |

For PostgreSQL, use a SQLAlchemy psycopg 3 URL such as:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

Never commit `.env` or production credentials.

## PostgreSQL setup

For a new hosted PostgreSQL database:

1. Create a database.
2. Apply `migrations/001_initial.sql` once using the provider's SQL console.
3. Set `DATABASE_URL` using the `postgresql+psycopg://` scheme.
4. Set `APP_ENV=production`.
5. Set a unique `JWT_SECRET` of at least 32 characters.
6. Set `AUTO_CREATE_TABLES=false`.
7. Configure `CORS_ORIGINS` and `ALLOWED_HOSTS` for the deployed application hostname.

Do not use the local SQLite database for production. Keep the migration and ORM schema aligned when changing models.

## Tests

Run:

```bash
pytest -q
```

The automated suite uses an isolated in-memory SQLite database. It does not prove production PostgreSQL concurrency behavior. Verify the concurrency-sensitive capacity rule against the target PostgreSQL provider before production use.

## Vercel deployment

This repository includes a root `index.py` exporting the FastAPI instance, which Vercel's FastAPI framework detection recognizes. Vercel serves `public/**` assets through its CDN, while FastAPI handles application routes including `/api/v1/*`. The minimal `vercel.json` only supplies schema validation; no catch-all rewrite is required.

In Vercel Project Settings, configure the environment variables listed above. For production, use a persistent hosted PostgreSQL database and apply the SQL migration before the first request. Set:

- `APP_ENV=production`
- `DATABASE_URL=postgresql+psycopg://...`
- `JWT_SECRET` to a unique random value (32+ characters)
- `AUTO_CREATE_TABLES=false`
- `CORS_ORIGINS` to your deployed origin
- `ALLOWED_HOSTS` to your Vercel hostname (or the exact custom domain)

Deployments and database connectivity must be tested in the actual Vercel project. This source package cannot verify your Vercel account, database credentials, project settings, or live deployment.

## API reference

- Browser application: `/`
- Health check: `/health`
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

See `docs/API_EXAMPLES.md` for request examples, `docs/AI_USAGE.md` for the AI assistance disclosure, `docs/DEMO_SCRIPT.md` for a recording walkthrough, `docs/screenshots/README.md` for screenshot requirements, and `docs/SECURITY_CHECKLIST.md` for security verification items.

## Security and limitations

- Organization access is enforced in application queries; database-level Row Level Security is not configured.
- Login requires organization ID, email, and password because the same email may exist in more than one organization.
- JWTs are stored in browser `sessionStorage` by this lightweight frontend. This is not equivalent to an HttpOnly secure-cookie session design.
- Rate limiting, email verification, password reset, audit logging, database backups, and production incident monitoring are not implemented.
- The project uses synchronous SQLAlchemy, not async database operations.
- A successful local test run does not establish a production security review or a live Vercel deployment.

## Project documentation

- `docs/PRD.md`
- `docs/ARCHITECTURE.md`
- `docs/DESIGN.md`
- `docs/RULES.md`
- `docs/MEMORY.md`
- `docs/API_EXAMPLES.md`
- `docs/SECURITY_CHECKLIST.md`
