import json
from pathlib import Path

class TaxonomyError(ValueError): pass

class Taxonomy:
    def __init__(self, path: str = "data/knowledge_taxonomy.json"):
        self.data = json.loads(Path(path).read_text(encoding="utf-8"))
        self.version = self.data["version"]
        self.nodes = {n["id"]: n for n in self.data["nodes"]}
        self.validate()

    def validate(self):
        if len(self.nodes) != len(self.data["nodes"]): raise TaxonomyError("duplicate node id")
        slugs = [n["slug"] for n in self.nodes.values()]
        if len(slugs) != len(set(slugs)): raise TaxonomyError("duplicate slug")
        for node in self.nodes.values():
            parent = node["parent_id"]
            if node["level"] == 1 and parent is not None: raise TaxonomyError("root parent")
            if node["level"] > 1 and (parent not in self.nodes or self.nodes[parent]["level"] != node["level"] - 1): raise TaxonomyError("invalid parent")

    def allowed(self, ids: list[str]) -> bool:
        return bool(ids) and all(i in self.nodes and self.nodes[i]["level"] > 1 for i in ids)

    def describe(self) -> str:
        return "\n".join(f'{n["id"]}: {n["name"]} (L{n["level"]})' for n in self.nodes.values() if n["level"] > 1)
