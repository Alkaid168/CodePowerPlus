"""画像公式：独立题目、最后一次非 CE 结果、父节点汇总与直接证据分开。"""
from app.knowledge import Taxonomy
from app.services.profile import build_profile


def record(problem_id, verdict, ids, version=''):
    return {'problem_id': problem_id, 'verdict': verdict, 'knowledge_ids': ids, 'taxonomy_version': version}


def test_mastery_formula_and_direct_evidence():
    taxonomy = Taxonomy()
    version = taxonomy.version
    profile = build_profile([
        record(1, 'WA', ['math.number-theory.prime'], version),
        record(1, 'AC', ['math.number-theory.prime'], version),
        record(2, 'TLE', ['math.number-theory.prime'], version),
    ], taxonomy)
    assert profile['skill_mastery']['math.number-theory.prime'] == 0.5
    assert profile['direct_skill_mastery'] == {'math.number-theory.prime': 0.5}
    assert profile['skill_mastery']['math.number-theory'] == 0.5
    assert profile['skill_mastery']['math'] == 0.5
    assert 'math.number-theory' not in profile['direct_skill_mastery']
    assert profile['submission_count'] == 3


def test_ce_is_ignored_and_latest_attempt_wins():
    taxonomy = Taxonomy()
    version = taxonomy.version
    profile = build_profile([
        record(1, 'AC', ['string.kmp'], version),
        record(1, 'CE', ['string.kmp'], version),
        record(2, 'AC', ['string.kmp'], version),
    ], taxonomy)
    # 两题都有最终 AC：(1+2)/(2+2) = 0.75；CE 不改变结果，也不额外计入证据。
    assert profile['skill_mastery']['string.kmp'] == 0.75
    skill = next(item for item in profile['skills'] if item['knowledge_id'] == 'string.kmp')
    assert skill['evidence_count'] == 2


def test_old_version_and_unknown_tags_are_unmapped():
    taxonomy = Taxonomy()
    profile = build_profile([
        record(1, 'AC', ['math.number-theory.prime'], 'old-version'),
        record(2, 'AC', ['invented'], taxonomy.version),
        record(3, 'AC', [], taxonomy.version),
    ], taxonomy)
    assert profile['skill_mastery'] == {}
    assert profile['direct_skill_mastery'] == {}
    assert profile['unmapped_submission_count'] == 3
    assert all(skill['evidence_count'] == 0 for skill in profile['skills'])


def test_profile_reports_every_node_with_unknown_mastery():
    taxonomy = Taxonomy()
    profile = build_profile([], taxonomy)
    assert len(profile['skills']) == len(taxonomy.nodes)
    assert profile['submission_count'] == 0
    assert profile['taxonomy_version'] == taxonomy.version
    assert profile['algorithm_version']
