"""清空题库数据（题目、分析、审核记录、提交）。

用法：
    python scripts/reset_data.py          # 预览：只显示将要删除的数量
    python scripts/reset_data.py --yes    # 真正执行，并自动备份数据库文件

备份写到系统临时目录，不污染项目文件夹；`--no-backup` 可跳过（不推荐）。
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import load_settings  # noqa: E402
from app.db import Database  # noqa: E402

# 先删子表再删父表，即使外键被关掉也不会留下孤儿行。
TABLES = ('analysis_reviews', 'problem_analyses', 'submissions', 'problems')


def counts(db: Database) -> dict[str, int]:
    return {table: db.query_one(f'SELECT COUNT(*) AS n FROM {table}')['n'] for table in TABLES}


def reset_sequences(db: Database) -> None:
    table = db.query_one("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'sqlite_sequence'")
    if table is None:
        return
    placeholders = ','.join('?' * len(TABLES))
    db.conn.execute(f'DELETE FROM sqlite_sequence WHERE name IN ({placeholders})', TABLES)


def main() -> int:
    parser = argparse.ArgumentParser(description='清空题库数据')
    parser.add_argument('--yes', action='store_true', help='确认执行删除')
    parser.add_argument('--no-backup', action='store_true', help='跳过数据库备份（不推荐）')
    args = parser.parse_args()

    settings = load_settings()
    path = Path(settings.db_path)
    db = Database(path)
    try:
        before = counts(db)
        for table, number in before.items():
            print(f'{table}: {number}')
        if not args.yes:
            print('这是预览，没有删除任何数据；确认后加 --yes 执行。')
            return 0

        backup = None
        if not args.no_backup and str(path) != ':memory:' and path.exists():
            backup = Path(tempfile.gettempdir()) / f'{path.stem}-backup-{datetime.now():%Y%m%d-%H%M%S}.db'
            db.close()
            shutil.copy2(path, backup)
            db = Database(path)

        with db.transaction():
            for table in TABLES:
                db.conn.execute(f'DELETE FROM {table}')
            reset_sequences(db)
        print(f'已清空题库，当前题目数：{counts(db)["problems"]}')
        print(f'备份文件：{backup}' if backup else '按要求未备份。')
        return 0
    finally:
        db.close()


if __name__ == '__main__':
    raise SystemExit(main())
