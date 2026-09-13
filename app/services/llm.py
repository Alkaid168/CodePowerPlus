import os
from app.config import settings


def build_prompt(description: str) -> str:
    return ("你是算法竞赛题目分析专家。请只输出合法 JSON（不要 Markdown），字段为 "
            "title,tags,difficulty,difficulty_reason,prerequisites,solution_idea,target_level,confidence。\n"
            f"题目：{description}")


def analyze_with_deepseek(description: str):
    from openai import OpenAI
    from .analyzer import parse_analysis
    if not settings.api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured")
    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
    response = client.chat.completions.create(model=settings.model, messages=[{"role": "user", "content": build_prompt(description)}], temperature=0)
    return parse_analysis(response.choices[0].message.content)
