def build_hint_prompt(problem: str, code: str, verdict: str) -> str:
    if verdict == "AC":
        return "恭喜你通过了这道题，可以尝试更高难度的题目。"
    return (f"你是程序设计辅导老师。评测结果：{verdict}。\n题目：{problem}\n代码：{code}\n"
            "请分级给出引导性提示，先指出思考方向，再指出可能的问题。不要直接给出完整代码。")


def extract_tutor_response(content: str) -> str:
    return content.strip()


def tutor_with_deepseek(problem: str, code: str, verdict: str) -> str:
    from openai import OpenAI
    from app.config import settings
    if not settings.api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured")
    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
    response = client.chat.completions.create(model=settings.model, messages=[{"role": "user", "content": build_hint_prompt(problem, code, verdict)}], temperature=0.2)
    return extract_tutor_response(response.choices[0].message.content)
