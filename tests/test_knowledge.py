from app.knowledge import Taxonomy

def test_taxonomy_validates_and_rejects_domain_only():
    taxonomy = Taxonomy()
    assert taxonomy.allowed(["math.number_theory.unique-factorization"])
    assert not taxonomy.allowed(["math"])

def test_taxonomy_has_versioned_nodes():
    taxonomy = Taxonomy()
    assert taxonomy.version
    assert taxonomy.nodes["graph.shortest-path.dijkstra"]["parent_id"] == "graph.shortest-path"
