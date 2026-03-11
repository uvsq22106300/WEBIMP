from graph_builder import GraphBuilder

builder = GraphBuilder()

validated_relations = builder.load_validated_relations("../output/validated_relations.json")
graph, audit_log = builder.build_graph_and_audit(validated_relations)

builder.save_json(graph, "../output/graph.json")
builder.save_json(audit_log, "../output/audit_log.json")
builder.export_rdf_turtle(graph, "../output/graph.ttl")
builder.export_neo4j_cypher(graph, "../output/neo4j.cypher")

print("Graphe et journal d'audit générés.")
print("Nombre de nœuds :", len(graph["nodes"]))
print("Nombre d'arêtes :", len(graph["edges"]))
print("Nombre d'entrées dans l'audit log :", len(audit_log))