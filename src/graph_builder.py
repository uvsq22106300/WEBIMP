import json
import os


class GraphBuilder:
    def load_validated_relations(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def infer_node_type(self, relation, is_subject=False):
        if is_subject:
            return "PERSON"

        mapping = {
            "birthDate": "DATE",
            "bornInCity": "CITY",
            "bornInCountry": "COUNTRY",
            "studiedField": "FIELD",
            "studiedAt": "ORG",
            "worksAt": "ORG",
            "marriedTo": "PERSON"
        }
        return mapping.get(relation, "ENTITY")

    def normalize_id(self, value):
        return value.replace(" ", "_").replace("'", "").replace("-", "_")

    def build_graph_and_audit(self, validated_relations):
        nodes = {}
        edges = []
        audit_log = []

        for rel in validated_relations:
            audit_entry = {
                "sent_id": rel["sent_id"],
                "subject": rel["subject"],
                "raw_relation": rel["raw_relation"],
                "normalized_relation": rel["normalized_relation"],
                "object": rel["object"],
                "status": rel["status"],
                "reason": rel["reason"],
                "evidence": rel["evidence"],
                "proof": rel["proof"],
                "justification": rel["justification"]
            }
            audit_log.append(audit_entry)

            if rel["status"] != "accepted":
                continue

            subject = rel["subject"]
            obj = rel["object"]
            relation = rel["normalized_relation"]

            if subject not in nodes:
                nodes[subject] = {
                    "id": self.normalize_id(subject),
                    "label": subject,
                    "type": self.infer_node_type(relation, is_subject=True)
                }

            if obj not in nodes:
                nodes[obj] = {
                    "id": self.normalize_id(obj),
                    "label": obj,
                    "type": self.infer_node_type(relation, is_subject=False)
                }

            edges.append({
                "source": self.normalize_id(subject),
                "target": self.normalize_id(obj),
                "relation": relation,
                "evidence": rel["evidence"]
            })

        graph = {
            "nodes": list(nodes.values()),
            "edges": edges
        }

        return graph, audit_log

    def save_json(self, data, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def export_rdf_turtle(self, graph, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        lines = [
            "@prefix ex: <http://example.org/kg/> .",
            "@prefix rel: <http://example.org/relation/> .",
            ""
        ]

        node_lookup = {node["id"]: node for node in graph["nodes"]}

        for edge in graph["edges"]:
            source_id = edge["source"]
            target_id = edge["target"]
            relation = edge["relation"]

            lines.append(
                f"ex:{source_id} rel:{relation} ex:{target_id} ."
            )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def export_neo4j_cypher(self, graph, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        lines = []

        for node in graph["nodes"]:
            node_id = node["id"]
            label = node["type"]
            name = node["label"].replace('"', '\\"')

            lines.append(
                f'MERGE (n:{label} {{id: "{node_id}"}}) '
                f'SET n.name = "{name}", n.type = "{label}";'
            )

        for edge in graph["edges"]:
            source = edge["source"]
            target = edge["target"]
            relation = edge["relation"].upper()
            evidence = edge["evidence"].replace('"', '\\"')

            lines.append(
                f'MATCH (a {{id: "{source}"}}), (b {{id: "{target}"}}) '
                f'MERGE (a)-[r:{relation}]->(b) '
                f'SET r.evidence = "{evidence}";'
            )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))