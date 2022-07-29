import csv
import json
import os
import pkg_resources

from pathlib import Path


def read_packages(path, config):
    ret = {}
    for p in Path(path).rglob('metadata.json'):
        d = load_metadata(p.parent)
        key = d["full_name"]
        if key not in config.exclude:
            ret[key] = d
    return ret


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


def load_metadata(path):
    dat = read_json(os.path.join(path, "metadata.json"))
    language = dat["language"]
    if language == "r":
        dat = load_metadata_r(path, dat)
    elif language == "python":
        dat = load_metadata_python(path, dat)
    elif language == "js":
        dat = load_metadata_js(path, dat)
    return dat


def load_metadata_r(path, dat):
    path_description = os.path.join(path, "description.json")
    if os.path.exists(path_description):
        desc = read_json(path_description)
        dat["name"] = desc.get("name", None)
        dat["version"] = desc["version"]
        dat["title"] = desc["title"]
        dat["description"] = desc["description"]
        dat["dependencies"] = desc["dependencies"]
        dat["authors"] = desc["authors"]
    return dat


def load_metadata_python(path, dat):
    path_requirements = os.path.join(path, "requirements.txt")
    dependencies = parse_requirements(path_requirements)
    # Parsing setup.py looks like a nightmare
    dat["name"] = dat["repo"] # should come from setup.py/pyproject.toml
    dat["version"] = None
    dat["title"] = None
    dat["description"] = None
    dat["dependencies"] = []
    dat["authors"] = []
    return dat


def load_metadata_js(path, dat):
    path_package = os.path.join(path, "package.json")
    if os.path.exists(path_package):
        pkg = read_json(path_package)
        dat["name"] = pkg.get("name", None)
        dat["version"] = pkg.get("version", None)
        dat["title"] = None
        dat["description"] = pkg.get("description", None)
        dat["dependencies"] = list(pkg.get("dependencies", {}).keys()) + \
            list(pkg.get("devDependencies", {}).keys())
        author = pkg.get("author", None)
        dat["authors"] = [author] if author else []
    return dat


def build_repo_map(dat):
    ret = {}
    for d in dat.values():
        language = d["language"]
        name = d.get("name", None)
        key = d["full_name"]
        if language and name:
            if language not in ret.keys():
                ret[language] = {}
            if name in ret[language].keys():
                prev = ret[language][name]
                raise Exception(f"Duplicate name {name} ({language}):" +
                                f" prev: {prev}, curr: {key}")
            ret[language][name] = key
    return ret


def resolve_dependencies(dat, repos):
    ret = {}
    for d in dat.values():
        language = d["language"]
        deps = {}
        for el in d.get("dependencies", []):
            if el in repos[language]:
                deps[el] = repos[language][el]
        d["dependencies"] = deps


def read_extra_metadata(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def add_extra_metadata(dat, config):
    metadata = read_extra_metadata(os.path.join(config.path, "metadata.csv"))
    for el in metadata:
        key = el["repo"]
        d = dat.get(key, None)
        if d:
            for k in ["domain", "authorship", "keyword", "doi"]:
                d[k] = el[k]


def write_repos(dat, config):
    dest = os.path.join(config.path, "repos.json")
    with open(dest, "w") as f:
        f.write(json.dumps(dat))


def parse_requirements(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            dependencies = \
                [str(req) for req in pkg_resources.parse_requirements(f)]
    else:
        depenencies = []
    return dependencies
