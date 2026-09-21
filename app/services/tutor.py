"""代码辅导：按评测结果给出分级提示。

设计约束（写进提示词，也写进产品说明）：默认不给完整代码，
先指出思考方向，再指出可能的问题，避免直接替学生写完。
"""
from __future__ import annotations

from app.errors import ModelUnavailable

VERDICT_HINT = {
    'WA': '答案错误通常来自边界条件、初始化或状态转移。',
    'TLE': '超时通常来自复杂度过高或常数过大。',
    'MLE': '内存超限通常来自数组开得过大或数据结构选择不当。',
    'RE': '运行时错误通常来自越界、除零或递归过深。',
    'CE': '编译错误先读第一条报错，定位行号。',
}


def build_hint_prompt(problem: str, code: str, verdict: str) -> str:
    if verdict == 'AC':
        return '这道题已经通过。可以尝试总结解法要点，或挑战更高难度、同类知识点的题目。'
    focus = VERDICT_HINT.get(verdict, '先定位最可疑的一步。')
    return (
        f'你是程序设计辅导老师。评测结果：{verdict}。{focus}\n'
        f'题目：\n{problem}\n\n学生代码：\n{code}\n\n'
        '请分三级给出提示：第一层只给思考方向，第二层指出可能出问题的代码位置，'
        '第三层给出验证思路。不要直接给出完整正确代码，也不要编造题面里没有的条件。'
    )


def tutor_with_model(problem: str, code: str, verdict: str, settings) -> str:
    from openai import OpenAI, OpenAIError

    if not settings.model_configured:
        raise ModelUnavailable('尚未配置模型密钥，无法生成辅导提示')
    try:
        with OpenAI(api_key=settings.api_key, base_url=settings.base_url,
                    timeout=settings.request_timeout, max_retries=1) as client:
            response = client.chat.completions.create(
                model=settings.model, temperature=0.2,
                messages=[{'role': 'user', 'content': build_hint_prompt(problem, code, verdict)}])
    except OpenAIError as exc:
        raise ModelUnavailable('模型辅导暂不可用，请稍后重试') from exc
    except ModelUnavailable:
        raise
    except Exception as exc:  # 代理或依赖问题同样按“模型不可用”返回 503
        raise ModelUnavailable(f'模型客户端初始化失败：{type(exc).__name__}') from exc
    return (response.choices[0].message.content or '').strip()
