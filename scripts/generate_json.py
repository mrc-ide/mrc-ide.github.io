import base64
import json
import os
import re
from ghapi.all import GhApi, paged
import emoji_data_python


class Repo(dict):
    def __init__(self, dat):
        packages = []
        try:
            desc = base64.b64decode(
                api.repos.get_content("mrc-ide",
                                      dat["name"],
                                      "DESCRIPTION"
                                      )["content"]
            ).decode("utf-8")
            m = re.search('(Remotes\:)((\s+.*\n)+)', desc)
            packages = m.group(2).split("\n")
            packages = [re.sub(r"@.*|,|\s+", "", p) for p in packages if
                        len(p) > 1]
        except:
            pass
        finally:
            description = dat["description"]
            if description is not None:
                description = emoji_data_python.replace_colons(description)
            dict.__init__(self,
                          url=dat["html_url"],
                          name=dat["name"],
                          full_name=dat["full_name"],
                          description=description,
                          packages=packages)


api = GhApi(token=os.environ["GITHUB_TOKEN"])

repos = []


def add_repos_for_org(org_name):
    pages = paged(api.repos.list_for_org, per_page=100, org=org_name)
    for page in pages:
        for r in page:
            if r["language"] == "R":
                repos.append(Repo(r))


add_repos_for_org("reside-ic")
add_repos_for_org("mrc-ide")

nodes = []
edges = []
for r in repos:
    if len(r["packages"]) > 0:
        if r["full_name"] not in [n["id"] for n in nodes]:
            nodes.append({"id": r["full_name"], "label": r["name"]})
        for p in r["packages"]:
            if p not in [n["id"] for n in nodes]:
                nodes.append({"id": p, "label": re.sub(r".*\/", "", p)})
            edges.append({"from": r["full_name"], "to": p})

with open('./static/repos.json', 'w') as outfile:
    outfile.write(json.dumps(repos))

with open('./static/graph.json', 'w') as outfile:
    outfile.write(json.dumps({"nodes": nodes, "edges": edges}))
