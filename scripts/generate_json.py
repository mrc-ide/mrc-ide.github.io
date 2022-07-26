import json
import os

from ghapi.all import GhApi, paged

from parse_repos import parse_r_package, parse_python_package, \
    parse_npm_package

# repos that we want to exclude
exclude_list = ["mrc-ide/odin-dust-plots",
                "mrc-ide.github.io",
                "mrc-ide/titanic2"]

org_names = ["mrc-ide", "vimc", "reside-ic"]

# make sure this is set to a token with no permissions
# so that private repos aren't returned
api = GhApi(token=os.environ["GITHUB_TOKEN"])

r_packages = []
py_packages = []
js_packages = []


def get_tree(org_name, repo_name):
    try:
        tree = api.git.get_tree(org_name,
                                repo_name,
                                "master")["tree"]
    except:
        try:
            tree = api.git.get_tree(org_name,
                                    repo_name,
                                    "main")["tree"]
        except:
            tree = None
    return tree


def add_repo(org_name, repo):
    if repo["full_name"] in exclude_list:
        return
    if repo["archived"]:
        return
    if repo["fork"]:
        return
    tree = get_tree(org_name, repo["name"])
    if tree:
        r_package = len([t for t in tree if
                         t["path"] == "DESCRIPTION"]) > 0
        py_package = len([t for t in tree if
                          t["path"] == "setup.py" or
                          t["path"] == "pyproject.toml"]) > 0
        npm_package = len([t for t in tree if
                           t["path"] == "package.json"]) > 0
        if r_package:
            r_packages.append(parse_r_package(api, org_name, repo))
        if py_package:
            py_packages.append(
                parse_python_package(api, org_name, repo))
        if npm_package:
            js_packages.append(parse_npm_package(api, org_name, repo))


def add_repos_for_org(org_name):
    pages = paged(api.repos.list_for_org, per_page=100, org=org_name)
    for page in pages:
        for repo in page:
            add_repo(org_name, repo)


def add_repo_for_org(org_name, repo_name):
    repo = api.repos.get(org_name, repo_name)
    add_repo(org_name, repo)


# add these 2 repos that are ours but hosted by external orgs
add_repo_for_org("ropensci", "cyphr")
add_repo_for_org("ropensci", "jsonvalidate")

# now add repos for all our orgs
for org in org_names:
    add_repos_for_org(org)


# filter package dependencies to only internal ones
py_names = set([p["name"] for p in py_packages])
r_names = set([p["name"] for p in r_packages])
js_names = set([p["name"] for p in js_packages])

for p in r_packages:
    p["packages"] = list(set(p["packages"]).intersection(r_names))

for p in py_packages:
    p["packages"] = list(set(p["packages"]).intersection(py_names))

for p in js_packages:
    p["packages"] = list(set(p["packages"]).intersection(js_names))

with open('./static/repos.json', 'w') as outfile:
    outfile.write(
        json.dumps({"r": r_packages, "py": py_packages, "js": js_packages})
    )

# dump out a file with all repo names, these then have to be manually sorted
# into categories and stored in categories.json
with open('./static/reponames.json', 'w') as outfile:
    outfile.write(
        json.dumps({"r": list(r_names), "py": list(py_names), "js": list(js_names)})
    )
