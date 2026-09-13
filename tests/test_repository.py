from app.repositories import ProblemRepository


def test_repository_saves_and_gets_problem():
    repo = ProblemRepository()
    item = repo.create("Two Sum", "给定数组")
    assert repo.get(item["id"])["title"] == "Two Sum"
