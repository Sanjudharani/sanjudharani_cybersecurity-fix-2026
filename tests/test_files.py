from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_path_traversal():
    response = client.get(
        "/files/../../../secret.txt"
    )

    assert response.status_code in [403,404]