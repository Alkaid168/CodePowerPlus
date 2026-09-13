import sqlite3
import json


class ProblemRepository:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("CREATE TABLE IF NOT EXISTS problems (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS problem_analyses (id INTEGER PRIMARY KEY, problem_id INTEGER NOT NULL, payload TEXT NOT NULL, FOREIGN KEY(problem_id) REFERENCES problems(id))")
        self.db.execute("CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, problem_id INTEGER NOT NULL, verdict TEXT NOT NULL, tags TEXT NOT NULL, code TEXT NOT NULL DEFAULT '', language TEXT NOT NULL DEFAULT 'unknown', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        columns = {row[1] for row in self.db.execute("PRAGMA table_info(submissions)")}
        for name, definition in (("code", "TEXT NOT NULL DEFAULT ''"), ("language", "TEXT NOT NULL DEFAULT 'unknown'"), ("created_at", "TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")):
            if name not in columns:
                self.db.execute(f"ALTER TABLE submissions ADD COLUMN {name} {definition}")
        self.db.commit()

    def create(self, title: str, description: str):
        cur = self.db.execute("INSERT INTO problems(title, description) VALUES (?, ?)", (title, description))
        self.db.commit()
        return dict(self.get(cur.lastrowid))

    def get(self, problem_id: int):
        row = self.db.execute("SELECT * FROM problems WHERE id = ?", (problem_id,)).fetchone()
        return dict(row) if row else None

    def save_analysis(self, problem_id: int, payload: dict):
        cur = self.db.execute("INSERT INTO problem_analyses(problem_id, payload) VALUES (?, ?)", (problem_id, json.dumps(payload, ensure_ascii=False)))
        self.db.commit()
        return {"id": cur.lastrowid, "problem_id": problem_id, **payload}

    def get_analysis(self, problem_id: int):
        row = self.db.execute("SELECT * FROM problem_analyses WHERE problem_id = ? ORDER BY id DESC LIMIT 1", (problem_id,)).fetchone()
        if not row:
            return None
        return json.loads(row["payload"])

    def add_submission(self, user_id, problem_id, verdict, tags):
        cur = self.db.execute("INSERT INTO submissions(user_id, problem_id, verdict, tags) VALUES (?, ?, ?, ?)", (user_id, problem_id, verdict, json.dumps(tags, ensure_ascii=False)))
        self.db.commit()
        return {"id": cur.lastrowid, "user_id": user_id, "problem_id": problem_id, "verdict": verdict, "tags": tags}

    def user_submissions(self, user_id):
        rows = self.db.execute("SELECT verdict, tags FROM submissions WHERE user_id = ?", (user_id,)).fetchall()
        return [{"problem_id": r["problem_id"], "verdict": r["verdict"], "tags": json.loads(r["tags"])} for r in rows]

    def all_problems(self):
        items = []
        for r in self.db.execute("SELECT * FROM problems ORDER BY id DESC").fetchall():
            item = dict(r)
            item["analysis"] = self.get_analysis(item["id"])
            items.append(item)
        return items

    def list_submissions(self, user_id=None):
        if user_id:
            rows = self.db.execute("SELECT * FROM submissions WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        else:
            rows = self.db.execute("SELECT * FROM submissions ORDER BY id DESC").fetchall()
        return [dict(r) | {"tags": json.loads(r["tags"])} for r in rows]
