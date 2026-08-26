from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ai_routes_exist():

    paths = set(
        app.openapi()["paths"].keys()
    )

    assert "/ai/ask" in paths
    assert "/ai/analyze-paper" in paths
    assert "/ai/analyze-themes" in paths
    assert "/ai/analyze-gaps" in paths
    assert "/ai/workflow" in paths


def test_ai_ask_validation():

    response = client.post(
        "/ai/ask",
        json={}
    )

    assert response.status_code == 422


def test_ai_ask_accepts_valid_request():

    response = client.post(
        "/ai/ask",
        json={
            "query": "population",
            "top_k": 3
        }
    )

    assert response.status_code in [
        200,
        429,
        502
    ]