from yattag import Doc
import json


def build_card(tag, text, r):
    with tag("div", klass="col-6"):
        with tag("div", klass="card"):
            with tag('a', href=r["url"]):
                text(r["full_name"])
            if r["language"] is not None:
                with tag('div'):
                    text("Language: ", r["language"])
            if r["description"] is not None:
                with tag('div'):
                    text(r["description"])
            if r["homepage"] is not None:
                with tag('a', href=r["homepage"]):
                    text(r["homepage"])
            if len(r["packages"]) > 0:
                with tag('span'):
                    text("Depends on:")
                with tag("ul"):
                    for p in r["packages"]:
                        with tag("li"):
                            text(p)


def generate_partial(repos, filename):
    doc, tag, text = Doc().tagtext()
    with tag('div', klass="row"):
        for r in repos:
            build_card(tag, text, r)

    with open(filename, 'w') as outfile:
        outfile.write(doc.getvalue())


with open('./static/repos.json', 'r') as f:
    repos = json.load(f)


with open('./static/categories.json', 'r') as f:
    categories = json.load(f)

research = [r for r in repos["r"] if r["name"] in categories["research"]]
frameworks = [r for r in repos["r"] if r["name"] in categories["framework"]]
tools = [r for r in repos["r"] if r["name"] in categories["devtool"]]

all = research + frameworks + tools

generate_partial(research, "./layouts/partials/research.html")
generate_partial(frameworks, "./layouts/partials/frameworks.html")
generate_partial(tools, "./layouts/partials/tools.html")
generate_partial(all, "./layouts/partials/all.html")
