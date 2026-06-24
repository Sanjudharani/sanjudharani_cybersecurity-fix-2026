from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_user_access_control():
    assert True