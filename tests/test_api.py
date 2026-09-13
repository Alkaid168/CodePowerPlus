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

def test_analyze_creates_and_persists_problem(monkeypatch):
    from app import main
    from app.schemas import ProblemAnalysis
    monkeypatch.setattr(main, "analyze_with_deepseek", lambda d: ProblemAnalysis(title="题目", tags=["dp"], difficulty=2, confidence=.9))
    response = TestClient(app).post("/api/problems/analyze", json={"title":"题目", "description":"描述"})
    assert response.status_code == 200
    body = response.json()
    assert body["problem"]["title"] == "题目"
    assert body["analysis"]["difficulty"] == 2

def test_get_missing_problem_returns_404():
    response = TestClient(app).get("/api/problems/999999")
    assert response.status_code == 404

def test_analyze_without_api_key_returns_service_unavailable(monkeypatch):
    from app import main
    monkeypatch.setattr(main, "analyze_with_deepseek", lambda _: (_ for _ in ()).throw(RuntimeError("DEEPSEEK_API_KEY is not configured")))
    response = TestClient(app).post("/api/problems/analyze", json={"description":"x"})
    assert response.status_code == 503

def test_submission_rejects_unknown_verdict():
    response = TestClient(app).post("/api/submissions", json={"user_id":"u","problem_id":1,"verdict":"UNKNOWN"})
    assert response.status_code == 422
