import json
import os
import re


class RelationExtractor:
    def __init__(self):
        self.current_person = None

    def load_sentences(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def clean_text(self, value):
        return value.strip().rstrip(".").strip()

    def remove_leading_article(self, value):
        value = self.clean_text(value)

        prefixes = ["la ", "le ", "les ", "l'", "du ", "de la ", "de l'"]
        lower_value = value.lower()

        for prefix in prefixes:
            if lower_value.startswith(prefix):
                return value[len(prefix):].strip()

        return value

    def split_fields(self, field_text):
        field_text = self.clean_text(field_text)
        parts = [p.strip() for p in re.split(r"\bet\b", field_text) if p.strip()]
        cleaned_parts = [self.remove_leading_article(part) for part in parts]
        return cleaned_parts

    def split_birth_place(self, birth_place_text):
        birth_place_text = self.clean_text(birth_place_text)

        city = None
        country = None

        if " en " in birth_place_text:
            parts = birth_place_text.split(" en ", 1)
            city = parts[0].strip()
            country = parts[1].strip()
        elif " aux " in birth_place_text:
            parts = birth_place_text.split(" aux ", 1)
            city = parts[0].strip()
            country = parts[1].strip()
        elif " au " in birth_place_text:
            parts = birth_place_text.split(" au ", 1)
            city = parts[0].strip()
            country = parts[1].strip()
        else:
            city = birth_place_text

        return city, country

    def make_candidate(self, sent_id, subject, raw_relation, obj, evidence):
        return {
            "sent_id": sent_id,
            "subject": self.clean_text(subject),
            "raw_relation": self.clean_text(raw_relation),
            "object": self.clean_text(obj),
            "evidence": self.clean_text(evidence)
        }

    def extract_relations(self, sentences):
        candidates = []

        for sentence in sentences:
            text = sentence["text"]
            sent_id = sentence["sent_id"]

            # 1) naissance
            birth_match = re.search(
                r"([A-ZÉÈÀÂÊÎÔÛÄËÏÖÜ][A-Za-zÉÈÀÂÊÎÔÛÄËÏÖÜéèàâêîôûç' -]+?) est né[e]? le ([0-9]{1,2} [A-Za-zéûôîàè]+ [0-9]{4}) à ([A-ZÉÈÀÂÊÎÔÛÄËÏÖÜ][A-Za-zÉÈÀÂÊÎÔÛÄËÏÖÜéèàâêîôûç' -]+)",
                text
            )
            if birth_match:
                person = self.clean_text(birth_match.group(1))
                birth_date = self.clean_text(birth_match.group(2))
                birth_place = self.clean_text(birth_match.group(3))

                city, country = self.split_birth_place(birth_place)
                self.current_person = person

                candidates.append(
                    self.make_candidate(sent_id, person, "est né le", birth_date, text)
                )

                if city:
                    candidates.append(
                        self.make_candidate(sent_id, person, "est né à", city, text)
                    )

                if country:
                    candidates.append(
                        self.make_candidate(sent_id, person, "est né dans le pays", country, text)
                    )

                continue

            # 2) études
            study_match = re.search(
                r"(?:Il|Elle) a étudié (.+?) à (.+)",
                text
            )
            if study_match and self.current_person:
                field_text = self.clean_text(study_match.group(1))
                study_place = self.remove_leading_article(study_match.group(2))
                fields = self.split_fields(field_text)

                for field in fields:
                    candidates.append(
                        self.make_candidate(sent_id, self.current_person, "a étudié", field, text)
                    )

                candidates.append(
                    self.make_candidate(sent_id, self.current_person, "a étudié à", study_place, text)
                )
                continue

            # 3) travail
            work_match = re.search(
                r"(?:Il|Elle) a travaillé à (.+)",
                text
            )
            if work_match and self.current_person:
                workplace = self.remove_leading_article(work_match.group(1))

                candidates.append(
                    self.make_candidate(sent_id, self.current_person, "a travaillé à", workplace, text)
                )
                continue

            # 4) mariage
            married_match = re.search(
                r"(?:Il|Elle) (?:est|était) marié[e]? à (.+)",
                text
            )
            if married_match and self.current_person:
                spouse = self.clean_text(married_match.group(1))

                candidates.append(
                    self.make_candidate(sent_id, self.current_person, "est marié à", spouse, text)
                )
                continue

        return candidates

    def save_relations(self, relations, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(relations, f, ensure_ascii=False, indent=4)