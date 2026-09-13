import sqlite3


class ProblemRepository:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("CREATE TABLE IF NOT EXISTS problems (id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL)")
        self.db.commit()

    def create(self, title: str, description: str):
        cur = self.db.execute("INSERT INTO problems(title, description) VALUES (?, ?)", (title, description))
        self.db.commit()
        return dict(self.get(cur.lastrowid))

    def get(self, problem_id: int):
        row = self.db.execute("SELECT * FROM problems WHERE id = ?", (problem_id,)).fetchone()
        return dict(row) if row else None
