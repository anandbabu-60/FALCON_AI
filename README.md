# AI Research & Project Collaboration Agent — Backend

A production-oriented FastAPI backend for managing M.Tech research projects, literature, datasets, research gaps, experiments, citations, milestones, and supervisor feedback.

## Folder structure

```text
backend/
├── alembic/                 # Database migration environment and revisions
├── app/
│   ├── api/                 # Versioned HTTP routes and dependencies
│   ├── core/                # Settings, security, logging
│   ├── database/            # SQLAlchemy engine/session/base
│   ├── middleware/          # Request logging middleware
│   ├── models/              # SQLAlchemy entities
│   ├── repositories/        # Reusable persistence abstraction
│   ├── schemas/             # Pydantic request/response DTOs
│   ├── services/            # Ownership-aware domain operations
│   └── main.py              # Application factory
├── tests/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── alembic.ini
```

## Quick start

> Use the `backend/app` package in this directory. The nested `ResearchPilot-AI/backend` folder is a legacy prototype and is not used by Docker Compose or the frontend.

```bash
cp .env.example .env
docker compose up --build
```

On Windows Command Prompt, use `copy .env.example .env` instead of `cp`.
Docker Desktop must be running before starting Compose.

Open Swagger UI at `http://localhost:8000/docs`. The health endpoint is `GET /health`.

### Google OAuth (optional)

The login page's **Continue with Google** button uses the backend OAuth callback. In Google Cloud Console, create a Web application OAuth client, configure the OAuth consent screen, and add this exact authorized redirect URI:

```text
http://localhost:8000/api/v1/auth/google/callback
```

Put the values in `backend/.env` (never commit this file):

```dotenv
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
FRONTEND_URL=http://localhost:5173
```

Restart the API and frontend after changing environment variables. Google redirects back to `/oauth/callback`, where the frontend stores the API JWT pair and opens the dashboard. If the credentials are omitted, the button shows a clear configuration message instead of a server error page.

For a local (non-Docker) run, create a PostgreSQL database, set `DATABASE_URL` in `.env`, then run:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

In Windows Command Prompt the activation command is `.venv\\Scripts\\activate.bat`;
in PowerShell it is `.\\.venv\\Scripts\\Activate.ps1`.

## API overview

All application endpoints are under `/api/v1` and require a Bearer access token unless noted.

| Area | Base endpoint | Operations |
|---|---|---|
| Authentication | `/auth/register`, `/auth/login`, `/auth/refresh` | Register, issue/refresh JWT pairs |
| Password recovery | `/auth/forgot-password`, `/auth/reset-password` | Email OTP reset with bcrypt password replacement |
| User | `/users/me` | Profile read, update, delete |
| Projects | `/projects` | Create, list/filter/search, read, update, delete |
| Project resources | `/projects/{project_id}/papers` | Full CRUD + pagination/search |
| | `/datasets`, `/tools`, `/gaps`, `/experiments`, `/citations`, `/roadmap`, `/reviews` | Full CRUD, project scoped |
| Documents | `/projects/{project_id}/documents` | Upload PDF/TXT, extract text, optionally index for RAG |
| AI | `/ai/chat`, `/ai/ask`, `/ai/analyze-*`, `/ai/workflow` | Authenticated Gemini/RAG analysis; project-scoped results can be persisted |
| Scholarly search | `/ai/research-sources` | Searches OpenAlex first and Crossref as a fallback; returns DOI, landing/PDF links, authors, year, publication, and abstracts, with optional project saving |
| AI history | `/projects/{project_id}/ai-artifacts` | List saved AI outputs for a project |
| Knowledge graph | `/knowledge-graph/*` | Authenticated UUID-safe Neo4j synchronization and graph reads |

Project list filters: `page`, `size`, `search`, `domain`, `project_status`. Resource list filters: `page`, `size`, `search` where the resource has a natural name/text field.

## Architecture notes

- Passwords are hashed with bcrypt; only hashes are stored.
- Short-lived access tokens and refresh tokens are signed using `SECRET_KEY`.
- All project and nested-resource operations verify ownership before persistence access.
- PostgreSQL foreign keys plus `ON DELETE CASCADE` retain referential integrity and clean associated research history when a project/account is intentionally removed.
- Alembic owns schema changes. Create future revisions with `alembic revision --autogenerate -m "description"`.
- LangChain, ChromaDB, Neo4j, PyMuPDF, and Redis dependencies are included as integration-ready packages. PDF/TXT uploads are stored under `STORAGE_DIR`, extracted with PyMuPDF/text decoding, and PDF chunks can be embedded into ChromaDB with project metadata for scoped retrieval.

### Optional local AI retrieval dependency

The core API can run without the native vector-search packages. Install the optional retrieval dependencies for PDF embeddings and ChromaDB indexing:

```bash
pip install -r requirements-ai.txt
```

On Windows with Python 3.13, this can require Microsoft C++ Build Tools because ChromaDB includes a native indexing extension.

## Production checklist

- Replace `SECRET_KEY` with a random value stored in a secrets manager.
- Never commit `.env` or paste its contents into issue trackers. Rotate Gemini, SMTP, Neo4j, and JWT secrets immediately if they have been shared.
- Set `ENVIRONMENT=production`, `DEBUG=false`, and explicit frontend `ALLOWED_ORIGINS`.
- Terminate TLS at a reverse proxy, use managed PostgreSQL/Redis, and run multiple Uvicorn workers.
- Add token revocation/rotation storage (Redis is already provisioned) if immediate logout or refresh-token invalidation is required.
