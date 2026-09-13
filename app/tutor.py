def build_hint_prompt(problem: str, code: str, verdict: str) -> str:
    if verdict == "AC":
        return "恭喜你通过了这道题，可以尝试更高难度的题目。"
    return (f"你是程序设计辅导老师。评测结果：{verdict}。\n题目：{problem}\n代码：{code}\n"
            "请分级给出引导性提示，先指出思考方向，再指出可能的问题。不要直接给出完整代码。")


def extract_tutor_response(content: str) -> str:
    return content.strip()


def tutor_with_deepseek(problem: str, code: str, verdict: str) -> str:
    import os
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    response = client.chat.completions.create(model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"), messages=[{"role": "user", "content": build_hint_prompt(problem, code, verdict)}], temperature=0.2)
    return extract_tutor_response(response.choices[0].message.content)
