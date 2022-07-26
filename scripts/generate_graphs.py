import json

with open('./static/repos.json', 'r') as f:
    repos = json.load(f)
    repos = repos["r"]


def add_node(nodes, name):
    if name not in [n["id"] for n in nodes]:
        nodes.append({"id": name, "label": name})


def generate_graph(focal_node, filename):
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


generate_graph("odin", "./static/odin-graph.json")
generate_graph("naomi", "./static/naomi-graph.json")
generate_graph("individual", "./static/individual-graph.json")
generate_graph("orderly", "./static/orderly-graph.json")
