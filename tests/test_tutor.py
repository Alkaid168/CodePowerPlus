from app.tutor import build_hint_prompt

def test_wrong_answer_gets_non_solution_hint():
    prompt = build_hint_prompt("两数之和", "int main(){}", "WA")
    assert "不要直接给出完整代码" in prompt
    assert "WA" in prompt

def test_accepted_submission_has_no_error_hint():
    assert "恭喜" in build_hint_prompt("x", "code", "AC")

def test_tutor_response_uses_model_content():
    from app.tutor import extract_tutor_response
    assert extract_tutor_response("model hint") == "model hint"
