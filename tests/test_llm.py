from app.services.llm import build_prompt


def test_build_prompt_requests_json_only():
    prompt = build_prompt("给定一个数组，求两数之和")
    assert "JSON" in prompt
    assert "给定一个数组" in prompt
    assert "math.number_theory.unique-factorization" in prompt
