import json
from app.services.analyzer import parse_analysis

def test_parse_analysis_extracts_json():
    result = parse_analysis(json.dumps({"title":"x","tags":["dp"],"difficulty":3,"confidence":0.9}))
    assert result.title == "x"

def test_parse_analysis_accepts_markdown_json():
    result = parse_analysis('```json\n{"title":"x","tags":[],"difficulty":1,"confidence":0.5}\n```')
    assert result.difficulty == 1
