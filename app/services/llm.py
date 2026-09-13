import os
from app.config import settings
from app.knowledge import Taxonomy


def build_prompt(description: str) -> str:
    taxonomy = Taxonomy()
    return ("你是算法竞赛题目分析专家。请只输出合法 JSON（不要 Markdown），字段为 "
            "title,tags,difficulty,difficulty_reason,prerequisites,solution_idea,target_level,confidence,primary_knowledge_ids,secondary_knowledge_ids,evidence,taxonomy_version。"
            "知识点只能从以下 ID 中选择，禁止创造新标签：\n" + taxonomy.describe() + "\n"
            f"题目：{description}")


def analyze_with_deepseek(description: str):
    from openai import OpenAI
    from .analyzer import parse_analysis
    if not settings.api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not configured")
    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)
    response = client.chat.completions.create(model=settings.model, messages=[{"role": "user", "content": build_prompt(description)}], temperature=0)
    result = parse_analysis(response.choices[0].message.content)
    taxonomy = Taxonomy()
    ids = result.primary_knowledge_ids + result.secondary_knowledge_ids
    if ids and not taxonomy.allowed(ids):
        raise RuntimeError("model returned knowledge IDs outside taxonomy")
    result.taxonomy_version = taxonomy.version
    return result
