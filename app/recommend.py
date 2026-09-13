def recommend(problems: list[dict], mastery: dict[str, float], solved_ids: list[int], limit: int = 10) -> list[dict]:
    solved = set(solved_ids)
    scored = []
    for problem in problems:
        if problem["id"] in solved:
            continue
        weakness = sum(1 - mastery.get(tag, 0.5) for tag in problem.get("tags", [])) / max(1, len(problem.get("tags", [])))
        target = 1 + 4 * (1 - weakness)
        fit = max(0, 1 - abs(problem.get("difficulty", 3) - target) / 4)
        scored.append(({**problem, "recommendation_score": round(0.7 * weakness + 0.3 * fit, 4)}, weakness))
    return [item for item, _ in sorted(scored, key=lambda x: x[0]["recommendation_score"], reverse=True)[:limit]]
