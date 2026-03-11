import json
from graphviz import Digraph


def load_graph(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def visualize_graph(graph):

    dot = Digraph(comment="Knowledge Graph")

    dot.attr(rankdir="LR")
    dot.attr("node", shape="ellipse", style="filled")

    # ajouter les noeuds
    for node in graph["nodes"]:

        color = "lightgrey"

        if node["type"] == "PERSON":
            color = "lightblue"

        elif node["type"] == "ORG":
            color = "orange"

        elif node["type"] == "CITY":
            color = "lightgreen"

        elif node["type"] == "COUNTRY":
            color = "green"

        elif node["type"] == "DATE":
            color = "pink"

        elif node["type"] == "FIELD":
            color = "violet"

        dot.node(node["id"], node["label"], fillcolor=color)

    # ajouter les relations
    for edge in graph["edges"]:

        dot.edge(
            edge["source"],
            edge["target"],
            label=edge["relation"]
        )

    dot.render("knowledge_graph", view=True, format="png")


if __name__ == "__main__":

    graph = load_graph("../output/graph.json")
    visualize_graph(graph)