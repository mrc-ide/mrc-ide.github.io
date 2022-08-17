import json
import os

from config import Config


def generate_graphs(root):
    config = Config(root)
    with open(os.path.join(config.static_dir, 'repos.json'), 'r') as f:
        repos = json.load(f)
    generate_entire_graph(repos, os.path.join(config.static_dir, "graph.json"))
    for graph in config.graphs:
        filename = f"{graph}-graph.json"
        generate_graph(repos, graph, os.path.join(config.static_dir, filename))


def add_node(nodes, name):
    if name not in [n["id"] for n in nodes]:
        nodes.append({"id": name, "label": name})


def generate_graph(repos, focal_node, filename):
    nodes = []
    edges = []
    for r in repos:
        name = r["name"]
        if name == focal_node or focal_node in r["dependencies"]:
            add_node(nodes, name)
            for p in r["dependencies"]:
                add_node(nodes, p)
                edges.append({"from": name, "to": p})
    with open(filename, 'w') as outfile:
        outfile.write(json.dumps({"nodes": nodes, "edges": edges}))


def generate_entire_graph(repos, filename):
    nodes = []
    edges = []
    for r in repos:
        name = r["name"]
        if len(r["dependencies"]) > 0:
            add_node(nodes, name)
            for p in r["dependencies"]:
                add_node(nodes, p)
                edges.append({"from": name, "to": p})
    with open(filename, 'w') as outfile:
        outfile.write(json.dumps({"nodes": nodes, "edges": edges}))
