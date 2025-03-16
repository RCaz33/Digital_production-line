from fastapi.testclient import TestClient
from app.main import app

client = TestClient()

def test_info():
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json() == {"name":"API pour prédictions","version":"1.0.0"}