from pydantic import BaseModel, Field


class ProblemAnalysis(BaseModel):
    title: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    difficulty: int = Field(ge=1, le=5)
    difficulty_reason: str = ""
    prerequisites: list[str] = Field(default_factory=list)
    solution_idea: str = ""
    target_level: str = ""
    confidence: float = Field(ge=0, le=1)
    primary_knowledge_ids: list[str] = Field(default_factory=list)
    secondary_knowledge_ids: list[str] = Field(default_factory=list)
    evidence: dict[str, str] = Field(default_factory=dict)
    taxonomy_version: str = ""
