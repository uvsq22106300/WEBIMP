from validator import RelationValidator

validator = RelationValidator()

normalized_relations = validator.load_normalized_relations("../output/normalized_relations.json")
validated_relations = validator.validate_relations(normalized_relations)
validator.save_validated_relations(validated_relations, "../output/validated_relations.json")

print("Relations validées :")
for rel in validated_relations:
    print(rel)