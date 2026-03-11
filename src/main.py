from preprocessing import Preprocessor
from ner import NERExtractor
from entity_linking import EntityLinker
from relation_extraction import RelationExtractor
from llm_normalization import LLMNormalizer
from validator import RelationValidator
from graph_builder import GraphBuilder


def main():
    print("1. Prétraitement...")
    preprocessor = Preprocessor()
    text = preprocessor.load_text("../data/sample.txt")
    sentences = preprocessor.split_into_sentences(text)
    preprocessor.save_sentences(sentences, "../output/sentences.json")

    print("2. NER...")
    ner_extractor = NERExtractor()
    entities = ner_extractor.extract_entities(sentences)
    ner_extractor.save_entities(entities, "../output/entities.json")

    print("3. Entity Linking...")
    linker = EntityLinker()
    linked_entities = linker.link_entities(entities)
    linker.save_linked_entities(linked_entities, "../output/linked_entities.json")

    print("4. Extraction des relations candidates...")
    relation_extractor = RelationExtractor()
    candidate_relations = relation_extractor.extract_relations(sentences)
    relation_extractor.save_relations(candidate_relations, "../output/candidate_relations.json")

    print("5. Normalisation contrôlée...")
    normalizer = LLMNormalizer()
    normalized_relations = normalizer.normalize_relations(candidate_relations)
    normalizer.save_normalized_relations(normalized_relations, "../output/normalized_relations.json")

    print("6. Validation automatique...")
    validator = RelationValidator()
    validated_relations = validator.validate_relations(normalized_relations)
    validator.save_validated_relations(validated_relations, "../output/validated_relations.json")

    print("7. Construction du graphe + journal d'audit...")
    builder = GraphBuilder()
    graph, audit_log = builder.build_graph_and_audit(validated_relations)

    builder.save_json(graph, "../output/graph.json")
    builder.save_json(audit_log, "../output/audit_log.json")
    builder.export_rdf_turtle(graph, "../output/graph.ttl")
    builder.export_neo4j_cypher(graph, "../output/neo4j.cypher")

    print("Pipeline terminé avec succès.")
    print("Fichiers générés dans ../output/")


if __name__ == "__main__":
    main()