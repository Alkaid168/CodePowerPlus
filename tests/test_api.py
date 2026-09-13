from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_problem_includes_analysis():
    from app.main import repository
    item = repository.create("API题", "描述")
    repository.save_analysis(item["id"], {"title":"API题", "tags":["dp"], "difficulty":2, "confidence":.8})
    response = TestClient(app).get(f"/api/problems/{item['id']}")
    assert response.json()["analysis"]["difficulty"] == 2
