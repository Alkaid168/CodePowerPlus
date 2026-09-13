import json
from app.schemas import ProblemAnalysis


def parse_analysis(raw: str) -> ProblemAnalysis:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return ProblemAnalysis.model_validate(json.loads(text))
