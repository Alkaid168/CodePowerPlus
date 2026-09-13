from app.repositories import ProblemRepository


def test_repository_saves_and_gets_problem():
    repo = ProblemRepository()
    item = repo.create("Two Sum", "给定数组")
    assert repo.get(item["id"])["title"] == "Two Sum"

def test_repository_saves_analysis():
    repo = ProblemRepository()
    item = repo.create("x", "d")
    saved = repo.save_analysis(item["id"], {"title":"x", "tags":["dp"],"difficulty":2,"confidence":.8})
    assert repo.get_analysis(item["id"])["difficulty"] == 2
