import base64
import json
import os
import re

from ghapi.all import GhApi, paged
import emoji_data_python

# repos that we want to exclude
# perhaps a better approach would be to tag all repos on GH
# that we want to include
exclude_list = ["mrc-ide/odin-dust-plots",
                "mrc-ide.github.io",
                "mrc-ide/titanic2"]

org_names = ["mrc-ide", "vimc", "reside-ic"]
org_regex = re.compile("(mrc-ide)|(vimc)|(reside-ic)")


class Repo(dict):
    def __init__(self, dat, deps):
        description = dat["description"]
        if description is not None:
            description = emoji_data_python.replace_colons(description)
        dict.__init__(self,
                      url=dat["html_url"],
                      name=dat["name"],
                      full_name=dat["full_name"],
                      description=description,
                      packages=deps,
                      language=dat["language"],
                      homepage=dat["homepage"])


def get_content_string(encoded):
    return base64.b64decode(encoded["content"]).decode("utf-8")


def parse_r_package(dat, description):
    desc = get_content_string(description)
    m = re.search('(Remotes\:)((\s+.*\n)+)', desc)
    if m:
        packages = m.group(2).split("\n")
        packages = [p for p in packages if re.search(org_regex, p)]
        packages = [re.sub(r"@.*|,|\s+", "", p) for p in packages if
                    len(p) > 1]
    else:
        packages = []
    return Repo(dat, packages)


def parse_python_package(dat, requirements):
    # if requirements:
    #     packages = get_content_string(requirements).split("\n")
    #     packages = [p for p in packages if len(p) > 0]
    # it's not so easy to work out which packages are internal ones here
    return Repo(dat, [])


def parse_npm_package(dat, package_json):
    json_obj = json.loads(get_content_string(package_json))
    deps = json_obj.get("dependencies")
    dev_deps = json_obj.get("devDependencies")
    packages = []
    if deps:
        packages.append(deps)
    if dev_deps:
        packages.append(dev_deps)
    return Repo(dat, [p for p in packages if "@reside-ic" in packages])


api = GhApi(token=os.environ["GITHUB_TOKEN"])

repos = []


def add_repos_for_org(org_name):
    pages = paged(api.repos.list_for_org, per_page=100, org=org_name)
    for page in pages:
        for repo in page:
            if repo["full_name"] in exclude_list:
                continue
            try:
                tree = api.git.get_tree(org_name,
                                        repo["name"],
                                        "master")["tree"]
            except:
                try:
                    tree = api.git.get_tree(org_name,
                                            repo["name"],
                                            "main")["tree"]
                except:
                    tree = None
            if tree:
                r_package = len([t for t in tree if
                                 t["path"] == "DESCRIPTION"]) > 0
                py_package = len([t for t in tree if
                                  t["path"] == "setup.py" or
                                  t["path"] == "pyproject.toml"]) > 0
                npm_package = len([t for t in tree if
                                   t["path"] == "package.json"]) > 0
                if r_package:
                    description = api.repos.get_content(org_name,
                                                        repo["name"],
                                                        "DESCRIPTION")
                    repos.append(parse_r_package(repo, description))
                if py_package:
                    if len([t for t in tree if
                            t["path"] == "requirements.txt"]) > 0:
                        requirements = api.repos.get_content(org_name,
                                                             repo["name"],
                                                             "requirements.txt")
                    else:
                        requirements = None
                    repos.append(parse_python_package(repo, requirements))
                if npm_package:
                    package_json = api.repos.get_content(org_name,
                                                         repo["name"],
                                                         "package.json")
                    repos.append(parse_npm_package(repo, package_json))


for org in org_names:
    add_repos_for_org(org)

nodes = []
edges = []
for r in repos:
    if len(r["packages"]) > 0:
        if r["full_name"] not in [n["id"] for n in nodes]:
            nodes.append({"id": r["full_name"], "label": r["name"]})
        for p in r["packages"]:
            if "mrc-ide" in p or "reside-ic" in p or "vimc" in p:
                if p not in [n["id"] for n in nodes]:
                    nodes.append({"id": p, "label": re.sub(r".*\/", "", p)})
                edges.append({"from": r["full_name"], "to": p})

with open('./static/repos.json', 'w') as outfile:
    outfile.write(json.dumps(repos))

with open('./static/graph.json', 'w') as outfile:
    outfile.write(json.dumps({"nodes": nodes, "edges": edges}))
