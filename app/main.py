from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.llm import analyze_with_deepseek
from app.repositories import ProblemRepository
from app.profile import calculate_skill_mastery
from app.recommend import recommend

repository = ProblemRepository("data/codepowerplus.db")

app = FastAPI(title="码力加加智能辅导系统", version="0.1.0")

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
    analysis = analyze_with_deepseek(request.description)
    problem = repository.create(request.title, request.description)
    repository.save_analysis(problem["id"], analysis.model_dump())
    return {"problem": problem, "analysis": analysis}

class ProblemCreate(BaseModel):
    title: str
    description: str

@app.post("/api/problems")
def create_problem(request: ProblemCreate):
    return repository.create(request.title, request.description)

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
    verdict: str
    tags: list[str] = []

@app.post("/api/submissions")
def create_submission(request: SubmissionCreate):
    return repository.add_submission(request.user_id, request.problem_id, request.verdict, request.tags)

@app.get("/api/users/{user_id}/profile")
def get_profile(user_id: str):
    records = repository.user_submissions(user_id)
    return {"user_id": user_id, "skill_mastery": calculate_skill_mastery(records), "submission_count": len(records)}

@app.get("/api/users/{user_id}/recommendations")
def get_recommendations(user_id: str):
    records = repository.user_submissions(user_id)
    mastery = calculate_skill_mastery(records)
    solved = []
    return {"user_id": user_id, "recommendations": recommend(repository.all_problems(), mastery, solved)}
