from llm_normalization import LLMNormalizer

normalizer = LLMNormalizer()

candidates = normalizer.load_candidate_relations("../output/candidate_relations.json")
normalized_relations = normalizer.normalize_relations(candidates)
normalizer.save_normalized_relations(normalized_relations, "../output/normalized_relations.json")

print("Relations normalisées :")
for rel in normalized_relations:
    print(rel)