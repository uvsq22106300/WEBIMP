import json
import os
import spacy


class Preprocessor:
    def __init__(self, model_name="fr_core_news_sm"):
        self.nlp = spacy.load(model_name)

    def load_text(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        text = text.replace("\n", " ")
        text = " ".join(text.split())

        return text.strip()

    def split_into_sentences(self, text, doc_id="doc_01"):
        doc = self.nlp(text)
        sentences = []

        for i, sent in enumerate(doc.sents, start=1):
            sentence_text = sent.text.strip()
            if sentence_text:
                sentences.append({
                    "doc_id": doc_id,
                    "sent_id": f"sent_{i:03}",
                    "text": sentence_text
                })

        return sentences

    def save_sentences(self, sentences, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sentences, f, ensure_ascii=False, indent=4)