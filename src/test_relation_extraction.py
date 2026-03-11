from relation_extraction import RelationExtractor

extractor = RelationExtractor()

sentences = extractor.load_sentences("../output/sentences.json")
relations = extractor.extract_relations(sentences)
extractor.save_relations(relations, "../output/relations.json")

print("Relations extraites :")
for relation in relations:
    print(relation)