import json
import os


class LLMNormalizer:
    def __init__(self):
        self.allowed_relations = [
            "birthDate",
            "bornInCity",
            "bornInCountry",
            "studiedField",
            "studiedAt",
            "worksAt",
            "marriedTo"
        ]

    def load_candidate_relations(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_prompt(self, candidate):
        return f"""
Tu es un module de normalisation sémantique pour un graphe de connaissances.

Tâche :
Choisir UNE relation normalisée parmi la liste fermée suivante :
{", ".join(self.allowed_relations)}

Entrée :
- Sujet : {candidate['subject']}
- Relation brute : {candidate['raw_relation']}
- Objet : {candidate['object']}
- Phrase source : {candidate['evidence']}

Contraintes :
1. Tu dois choisir uniquement une relation dans la liste autorisée.
2. Tu dois t'appuyer uniquement sur la phrase source.
3. Tu dois fournir une preuve textuelle.
4. Tu ne dois rien inventer.

Format attendu :
relation=<relation_autorisee>; preuve=<extrait>; justification=<raison courte>
""".strip()

    def normalize_candidate(self, candidate):
        raw_relation = candidate["raw_relation"].strip().lower()
        obj = candidate["object"].strip()
        evidence = candidate["evidence"].strip()

        normalized_relation = None
        justification = ""

        if raw_relation == "est né le":
            normalized_relation = "birthDate"
            justification = "La relation brute indique une date de naissance."

        elif raw_relation == "est né à":
            normalized_relation = "bornInCity"
            justification = "La relation brute indique un lieu de naissance de type ville."

        elif raw_relation == "est né dans le pays":
            normalized_relation = "bornInCountry"
            justification = "La relation brute indique un pays de naissance."

        elif raw_relation == "a étudié":
            normalized_relation = "studiedField"
            justification = "La relation brute indique un domaine d'étude."

        elif raw_relation == "a étudié à":
            normalized_relation = "studiedAt"
            justification = "La relation brute indique un établissement d'étude."

        elif raw_relation == "a travaillé à":
            normalized_relation = "worksAt"
            justification = "La relation brute indique un lieu de travail ou une organisation."

        elif raw_relation == "est marié à":
            normalized_relation = "marriedTo"
            justification = "La relation brute indique un lien matrimonial."

        if normalized_relation not in self.allowed_relations:
            normalized_relation = None
            justification = "Aucune relation autorisée correspondante."

        result = {
            "sent_id": candidate["sent_id"],
            "subject": candidate["subject"],
            "raw_relation": candidate["raw_relation"],
            "object": candidate["object"],
            "evidence": evidence,
            "prompt": self.build_prompt(candidate),
            "normalized_relation": normalized_relation,
            "proof": evidence,
            "justification": justification,
            "status": "normalized" if normalized_relation else "unmapped"
        }

        return result

    def normalize_relations(self, candidates):
        normalized_relations = []

        for candidate in candidates:
            normalized = self.normalize_candidate(candidate)
            normalized_relations.append(normalized)

        return normalized_relations

    def save_normalized_relations(self, normalized_relations, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(normalized_relations, f, ensure_ascii=False, indent=4)