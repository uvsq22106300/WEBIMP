import json
import os
import re


class RelationValidator:
    def __init__(self):
        self.schema = {
            "birthDate": {"domain": "PERSON", "range": "DATE"},
            "bornInCity": {"domain": "PERSON", "range": "CITY"},
            "bornInCountry": {"domain": "PERSON", "range": "COUNTRY"},
            "studiedField": {"domain": "PERSON", "range": "FIELD"},
            "studiedAt": {"domain": "PERSON", "range": "ORG"},
            "worksAt": {"domain": "PERSON", "range": "ORG"},
            "marriedTo": {"domain": "PERSON", "range": "PERSON"}
        }

        self.known_countries = {
            "Allemagne", "Pologne", "États-Unis", "France", "Italie",
            "Espagne", "Belgique", "Suisse", "Canada", "Maroc"
        }

        self.known_org_keywords = [
            "Université", "University", "Sorbonne", "École",
            "Harvard", "Princeton", "Maison-Blanche", "ETH"
        ]

        self.known_fields = {
            "physique", "chimie", "droit", "mathématiques",
            "économie", "biologie", "informatique"
        }

    def load_normalized_relations(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def infer_subject_type(self, subject):
        return "PERSON"

    def infer_object_type(self, relation, obj):
        obj = obj.strip()

        if relation == "birthDate":
            if re.match(r"^\d{1,2} [A-Za-zéèêàâîôûùçÉÈÊÀÂÎÔÛÙÇ\-]+ \d{4}$", obj):
                return "DATE"
            return "UNKNOWN"

        if relation == "bornInCountry":
            if obj in self.known_countries:
                return "COUNTRY"
            return "COUNTRY"

        if relation == "bornInCity":
            return "CITY"

        if relation == "studiedField":
            cleaned = obj.lower().strip()
            if cleaned in self.known_fields:
                return "FIELD"
            return "FIELD"

        if relation in ["studiedAt", "worksAt"]:
            for keyword in self.known_org_keywords:
                if keyword.lower() in obj.lower():
                    return "ORG"
            return "ORG"

        if relation == "marriedTo":
            if len(obj.split()) >= 2:
                return "PERSON"
            return "PERSON"

        return "UNKNOWN"

    def evidence_is_present(self, proof, evidence):
        if not proof or not evidence:
            return False

        proof_clean = proof.strip().lower()
        evidence_clean = evidence.strip().lower()

        return proof_clean in evidence_clean

    def validate_relations(self, normalized_relations):
        validated_relations = []

        for rel in normalized_relations:
            result = {
                "sent_id": rel["sent_id"],
                "subject": rel["subject"],
                "raw_relation": rel["raw_relation"],
                "normalized_relation": rel["normalized_relation"],
                "object": rel["object"],
                "evidence": rel["evidence"],
                "proof": rel["proof"],
                "justification": rel["justification"],
                "status": "rejected",
                "reason": ""
            }

            relation = rel.get("normalized_relation")

            if rel.get("status") != "normalized":
                result["reason"] = "Relation non normalisée"
                validated_relations.append(result)
                continue

            if relation not in self.schema:
                result["reason"] = "Relation non autorisée par le schéma"
                validated_relations.append(result)
                continue

            subject_type = self.infer_subject_type(rel["subject"])
            object_type = self.infer_object_type(relation, rel["object"])

            expected_domain = self.schema[relation]["domain"]
            expected_range = self.schema[relation]["range"]

            if subject_type != expected_domain:
                result["reason"] = (
                    f"Type du sujet invalide : attendu {expected_domain}, trouvé {subject_type}"
                )
                validated_relations.append(result)
                continue

            if object_type != expected_range:
                result["reason"] = (
                    f"Type de l'objet invalide : attendu {expected_range}, trouvé {object_type}"
                )
                validated_relations.append(result)
                continue

            if not self.evidence_is_present(rel["proof"], rel["evidence"]):
                result["reason"] = "Preuve textuelle absente de la phrase source"
                validated_relations.append(result)
                continue

            result["status"] = "accepted"
            result["reason"] = "Relation valide"
            validated_relations.append(result)

        return validated_relations

    def save_validated_relations(self, validated_relations, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(validated_relations, f, ensure_ascii=False, indent=4)