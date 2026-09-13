from pydantic import ValidationError
import pytest
from app.schemas import ProblemAnalysis

def test_problem_analysis_accepts_valid_payload():
    item = ProblemAnalysis(title="Two Sum", tags=["数组"], difficulty=2, confidence=0.8)
    assert item.difficulty == 2

def test_problem_analysis_rejects_invalid_difficulty():
    with pytest.raises(ValidationError):
        ProblemAnalysis(title="x", tags=[], difficulty=6, confidence=0.5)
