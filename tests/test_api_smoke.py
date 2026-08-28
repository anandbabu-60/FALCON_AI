from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models.user import User


def test_authenticated_project_and_document_flow():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    def override_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    db = session_factory()
    db.add(User(email="smoke@example.com", full_name="Smoke Test", password_hash=hash_password("SecurePass123"), is_active=True))
    db.commit()
    db.close()
    client = TestClient(app)
    try:
        assert client.post("/api/v1/ai/chat", json={"message": "hello"}).status_code in {401, 403}
        login = client.post("/api/v1/auth/login", json={"email": "  SMOKE@EXAMPLE.COM ", "password": "SecurePass123"})
        assert login.status_code == 200
        client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
        project = client.post("/api/v1/projects", json={"title": "Smoke Project", "research_idea": "A sufficiently detailed smoke-test research idea", "domain": "AI", "status": "draft"})
        assert project.status_code == 201
        project_id = project.json()["id"]
        projects = client.get("/api/v1/projects")
        assert projects.status_code == 200
        assert projects.json()["items"][0]["title"] == "Smoke Project"
        roadmap = client.get(f"/api/v1/projects/{project_id}/roadmap")
        assert roadmap.status_code == 200
        assert roadmap.json()["total"] == 4
        document = client.post(f"/api/v1/projects/{project_id}/documents", files={"file": ("notes.txt", b"Research notes", "text/plain")})
        assert document.status_code == 201
        assert document.json()["status"] == "ready"
        assert client.get(f"/api/v1/projects/{project_id}/documents").status_code == 200
        assert client.get(f"/api/v1/projects/{project_id}/ai-artifacts").status_code == 200
    finally:
        app.dependency_overrides.clear()
