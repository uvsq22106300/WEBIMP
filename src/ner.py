import json
import os
import spacy


class NERExtractor:
    def __init__(self, model_name="fr_core_news_sm"):
        self.nlp = spacy.load(model_name)

    def load_sentences(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def extract_entities(self, sentences):
        all_entities = []

        for sentence in sentences:
            doc = self.nlp(sentence["text"])

            for ent in doc.ents:
                all_entities.append({
                    "doc_id": sentence["doc_id"],
                    "sent_id": sentence["sent_id"],
                    "text": sentence["text"],
                    "mention": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })

        return all_entities

    def save_entities(self, entities, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(entities, f, ensure_ascii=False, indent=4)