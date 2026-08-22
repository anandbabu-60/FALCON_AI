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

```bash
cp .env.example .env
docker compose up --build
```

Open Swagger UI at `http://localhost:8000/docs`. The health endpoint is `GET /health`.

For a local (non-Docker) run, create a PostgreSQL database, set `DATABASE_URL` in `.env`, then run:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## API overview

All application endpoints are under `/api/v1` and require a Bearer access token unless noted.

| Area | Base endpoint | Operations |
|---|---|---|
| Authentication | `/auth/register`, `/auth/login`, `/auth/refresh` | Register, issue/refresh JWT pairs |
| User | `/users/me` | Profile read, update, delete |
| Projects | `/projects` | Create, list/filter/search, read, update, delete |
| Project resources | `/projects/{project_id}/papers` | Full CRUD + pagination/search |
| | `/datasets`, `/tools`, `/gaps`, `/experiments`, `/citations`, `/roadmap`, `/reviews` | Full CRUD, project scoped |

Project list filters: `page`, `size`, `search`, `domain`, `project_status`. Resource list filters: `page`, `size`, `search` where the resource has a natural name/text field.

## Architecture notes

- Passwords are hashed with bcrypt; only hashes are stored.
- Short-lived access tokens and refresh tokens are signed using `SECRET_KEY`.
- All project and nested-resource operations verify ownership before persistence access.
- PostgreSQL foreign keys plus `ON DELETE CASCADE` retain referential integrity and clean associated research history when a project/account is intentionally removed.
- Alembic owns schema changes. Create future revisions with `alembic revision --autogenerate -m "description"`.
- LangChain, ChromaDB, Neo4j, PyMuPDF, and Redis dependencies are included as integration-ready packages; keep their client adapters in `app/services/` when AI retrieval/PDF ingestion features are added.

### Optional AI retrieval dependency

The core API does not require ChromaDB yet. Install it only when vector-search ingestion is implemented:

```bash
pip install -r requirements-ai.txt
```

On Windows with Python 3.13, this can require Microsoft C++ Build Tools because ChromaDB includes a native indexing extension.

## Production checklist

- Replace `SECRET_KEY` with a random value stored in a secrets manager.
- Set `ENVIRONMENT=production`, `DEBUG=false`, and explicit frontend `ALLOWED_ORIGINS`.
- Terminate TLS at a reverse proxy, use managed PostgreSQL/Redis, and run multiple Uvicorn workers.
- Add token revocation/rotation storage (Redis is already provisioned) if immediate logout or refresh-token invalidation is required.
