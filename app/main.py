from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Literal
from app.services.llm import analyze_with_deepseek
from app.repositories import ProblemRepository
from app.profile import calculate_skill_mastery
from app.recommend import recommend
from app.tutor import build_hint_prompt, tutor_with_deepseek

repository = ProblemRepository("data/codepowerplus.db")

app = FastAPI(title="码力加加智能辅导系统", version="0.1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def homepage():
    return FileResponse("app/static/index.html")

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", message="码力加加服务运行正常")

class AnalyzeRequest(BaseModel):
    title: str = "未命名题目"
    description: str

@app.post("/api/problems/analyze")
def analyze_problem(request: AnalyzeRequest):
    try:
        analysis = analyze_with_deepseek(request.description)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    problem = repository.create(request.title, request.description)
    repository.save_analysis(problem["id"], analysis.model_dump())
    return {"problem": problem, "analysis": analysis}

class ProblemCreate(BaseModel):
    title: str
    description: str

@app.post("/api/problems")
def create_problem(request: ProblemCreate):
    return repository.create(request.title, request.description)

@app.get("/api/problems")
def list_problems():
    return {"items": repository.all_problems()}

@app.get("/api/problems/{problem_id}")
def get_problem(problem_id: int):
    problem = repository.get(problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="problem_not_found")
    problem["analysis"] = repository.get_analysis(problem_id)
    return problem

class SubmissionCreate(BaseModel):
    user_id: str
    problem_id: int
    verdict: Literal["AC", "WA", "TLE", "MLE", "RE", "CE"]
    tags: list[str] = []
    code: str = ""
    language: str = "unknown"

@app.post("/api/submissions")
def create_submission(request: SubmissionCreate):
    if repository.get(request.problem_id) is None:
        raise HTTPException(status_code=404, detail="problem_not_found")
    result = repository.add_submission(request.user_id, request.problem_id, request.verdict, request.tags)
    repository.db.execute("UPDATE submissions SET code=?, language=? WHERE id=?", (request.code, request.language, result["id"]))
    repository.db.commit()
    result.update(code=request.code, language=request.language)
    return result

@app.get("/api/submissions")
def list_submissions(user_id: str | None = None):
    return {"items": repository.list_submissions(user_id)}

@app.get("/api/users/{user_id}/profile")
def get_profile(user_id: str):
    records = repository.user_submissions(user_id)
    return {"user_id": user_id, "skill_mastery": calculate_skill_mastery(records), "submission_count": len(records)}

@app.get("/api/users/{user_id}/recommendations")
def get_recommendations(user_id: str):
    records = repository.user_submissions(user_id)
    mastery = calculate_skill_mastery(records)
    solved = [r["problem_id"] for r in records if r["verdict"] == "AC"]
    return {"user_id": user_id, "recommendations": recommend(repository.all_problems(), mastery, solved)}

class TutorRequest(BaseModel):
    problem: str
    code: str
    verdict: str

@app.post("/api/tutor/hint")
def tutor_hint(request: TutorRequest):
    import os
    if os.getenv("DEEPSEEK_API_KEY"):
        return {"hint": tutor_with_deepseek(request.problem, request.code, request.verdict)}
    return {"prompt": build_hint_prompt(request.problem, request.code, request.verdict)}
