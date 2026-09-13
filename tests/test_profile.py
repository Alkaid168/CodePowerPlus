from app.profile import calculate_skill_mastery

def test_mastery_rewards_acceptance_and_penalizes_failure():
    records = [{"tags":["dp"],"verdict":"AC"},{"tags":["dp"],"verdict":"WA"}]
    result = calculate_skill_mastery(records)
    assert 0 < result["dp"] < 1

def test_mastery_is_empty_without_records():
    assert calculate_skill_mastery([]) == {}
