import json
import os
import time
import requests


class EntityLinker:
    def __init__(self, language="fr", search_limit=1, pause_seconds=0.2):
        self.api_url = "https://www.wikidata.org/w/api.php"
        self.language = language
        self.search_limit = search_limit
        self.pause_seconds = pause_seconds
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SemanticWebProject/1.0 (entity-linking educational project)"
        })

    def load_entities(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize_mention(self, mention):
        return mention.strip()

    def map_spacy_label(self, label):
        mapping = {
            "PER": "PERSON",
            "LOC": "LOCATION",
            "ORG": "ORG",
            "DATE": "DATE"
        }
        return mapping.get(label, label)

    def search_wikidata(self, mention):
        params = {
            "action": "wbsearchentities",
            "search": mention,
            "language": self.language,
            "format": "json",
            "limit": self.search_limit
        }

        try:
            response = self.session.get(self.api_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            results = data.get("search", [])

            if not results:
                return None

            best = results[0]

            return {
                "entity_id": best.get("id"),
                "entity_label": best.get("label"),
                "description": best.get("description"),
                "url": best.get("concepturi")
            }

        except requests.RequestException as e:
            return {
                "error": str(e)
            }

    def link_entities(self, entities):
        linked_entities = []

        for entity in entities:
            mention = self.normalize_mention(entity["mention"])
            mention_label = self.map_spacy_label(entity["label"])

            result = {
                "doc_id": entity["doc_id"],
                "sent_id": entity["sent_id"],
                "text": entity.get("text", ""),
                "mention": mention,
                "mention_label": mention_label,
                "start": entity["start"],
                "end": entity["end"],
                "linked": False,
                "entity_id": None,
                "entity_label": None,
                "description": None,
                "url": None,
                "source": "Wikidata"
            }

            wikidata_result = self.search_wikidata(mention)

            if wikidata_result:
                if "error" in wikidata_result:
                    result["description"] = wikidata_result["error"]
                else:
                    result["linked"] = True
                    result["entity_id"] = wikidata_result["entity_id"]
                    result["entity_label"] = wikidata_result["entity_label"]
                    result["description"] = wikidata_result["description"]
                    result["url"] = wikidata_result["url"]

            linked_entities.append(result)

            time.sleep(self.pause_seconds)

        return linked_entities

    def save_linked_entities(self, linked_entities, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(linked_entities, f, ensure_ascii=False, indent=4)