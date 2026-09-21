"""能力画像：把提交证据折算成每个知识点的掌握度。

规则（可解释的启发式，不是校准过的学习概率）：
1. 同一道题只取最后一次非 CE 结果，重复提交不产生额外证据；
2. 某个标签的分数 = (1 + 最终 AC 的题目数) / (2 + 有证据的题目数)；
3. 父节点分数是子树证据的汇总，单独算一份，不冒充每个子知识点已掌握；
4. 只有当前版本、已审核分析的提交才算证据，其余计入 unmapped。
"""
from __future__ import annotations

from collections import defaultdict

ALGORITHM_VERSION = 'independent-problem-evidence-v1'
EXPLANATION = '按独立题目的最后一次非编译错误结果估计；无证据为待评估，分数不是已校准的通过概率。'


def mastery_from_evidence(evidence: dict[str, list[bool]]) -> dict[str, float]:
    """掌握度公式的唯一实现：(1 + AC 题数) / (2 + 有证据题数)。"""
    return {tag: round((1 + sum(values)) / (2 + len(values)), 4)
            for tag, values in evidence.items() if values}


def latest_attempts(records: list[dict]) -> list[dict]:
    latest: dict = {}
    for index, record in enumerate(records):
        if record.get('verdict') == 'CE':
            continue
        latest[record.get('problem_id', f'record-{index}')] = record
    return list(latest.values())


def build_profile(records: list[dict], taxonomy) -> dict:
    def usable(record: dict) -> bool:
        ids = record.get('knowledge_ids') or []
        return record.get('taxonomy_version') == taxonomy.version and taxonomy.allowed(ids)

    evidence: dict[str, dict] = defaultdict(dict)
    direct: dict[str, dict] = defaultdict(dict)
    for index, record in enumerate(latest_attempts(records)):
        if not usable(record):
            continue
        problem_id = record.get('problem_id', index)
        ac = record['verdict'] == 'AC'
        targets = set(record['knowledge_ids'])
        for node_id in record['knowledge_ids']:
            direct[node_id][problem_id] = ac
            targets.update(ancestor['id'] for ancestor in taxonomy.ancestors(node_id))
        for node_id in targets:
            evidence[node_id][problem_id] = ac

    skills, mastery = [], {}
    for node_id, node in taxonomy.nodes.items():
        values = list(evidence[node_id].values())
        count = len(values)
        score = round((1 + sum(values)) / (2 + count), 4) if count else None
        if count:
            mastery[node_id] = score
        skills.append({'knowledge_id': node_id, 'name': node['name'], 'level': node['level'],
                       'mastery': score, 'evidence_count': count,
                       'direct_evidence_count': len(direct[node_id]),
                       'confidence': round(count / (count + 5), 4)})
    direct_mastery = mastery_from_evidence({node_id: list(values.values()) for node_id, values in direct.items()})
    return {
        'submission_count': len(records),
        'skill_mastery': mastery,
        'direct_skill_mastery': direct_mastery,
        'skills': skills,
        'taxonomy_version': taxonomy.version,
        'unmapped_submission_count': sum(not usable(record) for record in records),
        'algorithm_version': ALGORITHM_VERSION,
        'explanation': EXPLANATION,
    }
