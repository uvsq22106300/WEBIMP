from entity_linking import EntityLinker

linker = EntityLinker()

entities = linker.load_entities("../output/entities.json")
linked_entities = linker.link_entities(entities)
linker.save_linked_entities(linked_entities, "../output/linked_entities.json")

print("Entités liées :")
for entity in linked_entities:
    print(entity)