from yattag import Doc
import json

doc, tag, text = Doc().tagtext()


with open('./static/repos.json', 'r') as f:
    repos = json.load(f)


with tag('div', klass="row"):
    for r in repos:
        with tag("div", klass="col-6"):
            with tag("div", klass="card"):
                with tag('a', href=r["url"]):
                    text(r["full_name"])
                if r["language"] is not None:
                    with tag('div'):
                        text("Language: ",  r["language"])
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


with open('./layouts/partials/repos.html', 'w') as outfile:
    outfile.write(doc.getvalue())
