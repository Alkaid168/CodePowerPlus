import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.repositories import ProblemRepository

repo = ProblemRepository("data/codepowerplus.db")
samples = [
    ("两数之和", "给定整数数组和目标值，返回和为目标值的两个下标。"),
    ("最长递增子序列", "给定整数数组，求最长严格递增子序列长度。"),
    ("最短路", "给定带权图，求源点到各点的最短距离。"),
]
for title, description in samples:
    repo.create(title, description)
print(f"已写入 {len(samples)} 道示例题目")
