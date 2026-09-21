"""校验知识点介绍文件：键集合、长度、重复与套话。

用法：
    python scripts/check_notes.py <assignment.json> <notes.json>
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

MIN_LEN, MAX_LEN = 50, 200
BANNED = ('待补充', 'TODO', '本知识点', '本文将', '学习目标', '前置知识', '参考资料', 'http')


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    assignment = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
    notes_path = Path(sys.argv[2])
    if not notes_path.exists():
        print(f'缺少输出文件：{notes_path}')
        return 1
    notes = json.loads(notes_path.read_text(encoding='utf-8'))

    missing = [key for key in assignment if key not in notes]
    extra = [key for key in notes if key not in assignment]
    bad_type = [key for key, value in notes.items() if not isinstance(value, str)]
    length = {key: len(value) for key, value in notes.items() if isinstance(value, str)}
    too_short = sorted(key for key, size in length.items() if size < MIN_LEN)
    too_long = sorted(key for key, size in length.items() if size > MAX_LEN)
    duplicated = [text for text, count in Counter(notes.values()).items() if count > 1]
    banned_hits = {key: [word for word in BANNED if word in value]
                   for key, value in notes.items() if isinstance(value, str)
                   and any(word in value for word in BANNED)}
    same_as_name = [key for key, value in notes.items()
                    if isinstance(value, str) and value.strip() == str(assignment.get(key, '')).strip()]
    multiline = [key for key, value in notes.items() if isinstance(value, str) and '\n' in value]

    problems = 0
    for label, items in [('缺少节点', missing), ('多出节点', extra), ('类型错误', bad_type),
                         ('太短', too_short), ('太长', too_long), ('重复段落', duplicated),
                         ('套话', banned_hits), ('与名称相同', same_as_name), ('包含换行', multiline)]:
        if items:
            problems += 1
            preview = items[:8]
            print(f'{label}: {len(items)} 个 -> {preview}')
    sizes = list(length.values())
    print(f'共 {len(notes)} 条，长度 {min(sizes) if sizes else 0}–{max(sizes) if sizes else 0} 字')
    print('校验通过' if not problems else '存在问题，请修改后重跑')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
