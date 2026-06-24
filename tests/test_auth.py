from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sql_injection_login():
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com' --",
            "password": "x"
        }
    )

    assert response.status_code == 401