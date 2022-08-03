import json


def add_node(nodes, name):
    if name not in [n["id"] for n in nodes]:
        nodes.append({"id": name, "label": name})


def generate_graph(repos, focal_node, filename):
    nodes = []
    edges = []
    for r in repos:
        name = r["name"]
        if name == focal_node or focal_node in r["packages"]:
            add_node(nodes, name)
            for p in r["packages"]:
                add_node(nodes, p)
                edges.append({"from": name, "to": p})
    with open(filename, 'w') as outfile:
        outfile.write(json.dumps({"nodes": nodes, "edges": edges}))
