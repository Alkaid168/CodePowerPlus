from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.llm import analyze_with_deepseek
from app.repositories import ProblemRepository

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
