from fastapi.testclient import TestClient

from app.main import app
from app.seed import seed


def test_health():
    seed()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_seed_user():
    seed()
    client = TestClient(app)
    response = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "alice123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
