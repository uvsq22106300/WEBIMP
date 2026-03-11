from ner import NERExtractor

extractor = NERExtractor()

sentences = extractor.load_sentences("../output/sentence.json")
entities = extractor.extract_entities(sentences)
extractor.save_entities(entities, "../output/entities.json")

print("Entités détectées :")
for entity in entities:
    print(entity)