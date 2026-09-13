from app.recommend import recommend

def test_recommend_prefers_weak_skill_and_nearby_difficulty():
    problems = [{"id":1,"tags":["dp"],"difficulty":3},{"id":2,"tags":["graph"],"difficulty":5}]
    result = recommend(problems, {"dp":0.2,"graph":0.8}, solved_ids=[])
    assert result[0]["id"] == 1

def test_recommend_excludes_solved():
    assert recommend([{"id":1,"tags":["dp"],"difficulty":2}], {"dp":0.2}, [1]) == []
