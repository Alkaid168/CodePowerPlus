from collections import defaultdict


def calculate_skill_mastery(records: list[dict]) -> dict[str, float]:
    totals = defaultdict(float)
    counts = defaultdict(float)
    for record in records:
        weight = 1.0 if record.get("verdict") == "AC" else -0.35
        for tag in record.get("tags", []):
            totals[tag] += weight
            counts[tag] += 1
    return {tag: max(0.0, min(1.0, 0.5 + totals[tag] / (2 * counts[tag]))) for tag in counts}
