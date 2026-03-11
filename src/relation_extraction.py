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

        # séparer sur " et "
        parts = [p.strip() for p in re.split(r"\bet\b", field_text) if p.strip()]

        cleaned_parts = []
        for part in parts:
            part = part.strip()

            for prefix in ["la ", "le ", "les ", "l'"]:
                if part.lower().startswith(prefix):
                    part = part[len(prefix):]
                    break

            cleaned_parts.append(part.strip())

        return cleaned_parts

    def extract_birth_place(self, birth_place_text):
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

    def extract_relations(self, sentences):
        relations = []

        for sentence in sentences:
            text = sentence["text"]

            # 1. naissance : nom + date + lieu
            birth_match = re.search(
                r"([A-ZÉÈÀÂÊÎÔÛÄËÏÖÜ][A-Za-zÉÈÀÂÊÎÔÛÄËÏÖÜéèàâêîôûç' -]+?) est né[e]? le ([0-9]{1,2} [A-Za-zéûôîàè]+ [0-9]{4}) à ([A-ZÉÈÀÂÊÎÔÛÄËÏÖÜ][A-Za-zÉÈÀÂÊÎÔÛÄËÏÖÜéèàâêîôûç' -]+)",
                text
            )
            if birth_match:
                person = self.clean_text(birth_match.group(1))
                birth_date = self.clean_text(birth_match.group(2))
                birth_place = self.clean_text(birth_match.group(3))

                city, country = self.extract_birth_place(birth_place)

                self.current_person = person

                relations.append({
                    "sent_id": sentence["sent_id"],
                    "subject": person,
                    "relation": "birthDate",
                    "object": birth_date,
                    "evidence": text
                })

                if city:
                    relations.append({
                        "sent_id": sentence["sent_id"],
                        "subject": person,
                        "relation": "bornInCity",
                        "object": city,
                        "evidence": text
                    })

                if country:
                    relations.append({
                        "sent_id": sentence["sent_id"],
                        "subject": person,
                        "relation": "bornInCountry",
                        "object": country,
                        "evidence": text
                    })

                continue

            # 2. études
            study_match = re.search(
                r"(?:Il|Elle) a étudié (.+?) à (.+)",
                text
            )
            if study_match and self.current_person:
                field_text = self.clean_text(study_match.group(1))
                place = self.remove_leading_article(study_match.group(2))

                fields = self.split_fields(field_text)

                for field in fields:
                    relations.append({
                        "sent_id": sentence["sent_id"],
                        "subject": self.current_person,
                        "relation": "studiedField",
                        "object": field,
                        "evidence": text
                    })

                relations.append({
                    "sent_id": sentence["sent_id"],
                    "subject": self.current_person,
                    "relation": "studiedAt",
                    "object": place,
                    "evidence": text
                })
                continue

            # 3. travail
            work_match = re.search(
                r"(?:Il|Elle) a travaillé à (.+)",
                text
            )
            if work_match and self.current_person:
                workplace = self.remove_leading_article(work_match.group(1))

                relations.append({
                    "sent_id": sentence["sent_id"],
                    "subject": self.current_person,
                    "relation": "worksAt",
                    "object": workplace,
                    "evidence": text
                })
                continue

            # 4. mariage
            married_match = re.search(
                r"(?:Il|Elle) (?:est|était) marié[e]? à (.+)",
                text
            )
            if married_match and self.current_person:
                spouse = self.clean_text(married_match.group(1))

                relations.append({
                    "sent_id": sentence["sent_id"],
                    "subject": self.current_person,
                    "relation": "marriedTo",
                    "object": spouse,
                    "evidence": text
                })
                continue

        return relations

    def save_relations(self, relations, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(relations, f, ensure_ascii=False, indent=4)