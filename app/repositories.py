import sqlite3
import json


class ProblemRepository:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("CREATE TABLE IF NOT EXISTS problems (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS problem_analyses (id INTEGER PRIMARY KEY, problem_id INTEGER NOT NULL, payload TEXT NOT NULL, FOREIGN KEY(problem_id) REFERENCES problems(id))")
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
