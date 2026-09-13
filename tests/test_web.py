from fastapi.testclient import TestClient
from app.main import app

def test_homepage_is_available():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "码力加加" in response.text

def test_static_assets_are_available():
    client = TestClient(app)
    assert client.get("/static/app.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200
