from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="码力加加智能辅导系统", version="0.1.0")

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", message="码力加加服务运行正常")
