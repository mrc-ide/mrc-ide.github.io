import csv
import json
import os

import emoji_data_python
import pkg_resources

from pathlib import Path

from config import Config


def generate_json(path):
    config = Config(path)
    dat = read_packages(os.path.join(path, "data"), config)
    repos = build_repo_map(dat)
    resolve_dependencies(dat, repos)
    add_extra_metadata(dat, config)
    add_categories(dat, config)
    add_emojis(dat)
    write_repos(dat, config)


def read_packages(path, config):
    ret = {}
    for p in Path(path).rglob('metadata.json'):
        d = load_metadata(p.parent)
        key = d["full_name"]
        d["name"] = d["repo"]
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


## When doing this, we probably want to skip over dummy entries like:
## "What the Package Does (One Line, Title Case)"
## which is added by devtools
def load_metadata_r(path, dat):
    ignore_title = "What the package does (one paragraph)"
    ignore_description = "What the Package Does (one line, title case)"
    path_description = os.path.join(path, "description.json")
    if os.path.exists(path_description):
        desc = read_json(path_description)
        dat["name"] = desc.get("name", dat["repo"])
        dat["version"] = desc["version"]
        dat["title"] = desc["title"] \
            if desc["title"] != ignore_title else None
        dat["description"] = desc["description"] \
            if desc["description"] != ignore_description else None
        dat["dependencies"] = desc["dependencies"]
        dat["authors"] = desc["authors"]
    return dat


def load_metadata_python(path, dat):
    path_requirements = os.path.join(path, "requirements.txt")
    dependencies = parse_requirements(path_requirements)
    # Parsing setup.py looks like a nightmare
    dat["name"] = dat["repo"]  # should come from setup.py/pyproject.toml
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
        dat["name"] = pkg.get("name", dat["repo"])
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
        if language is None:
            if d["language_github"] is not None:
                language = d["language_github"].lower()
                d["language"] = language
        name = d.get("name", d["repo"])
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
    for d in dat.values():
        language = d["language"]
        deps = {}
        for el in d.get("dependencies", []):
            if el in repos[language]:
                deps[el] = repos[language][el]
        d["dependencies"] = deps
        d["used_by"] = []
    for d in dat.values():
        for el in d["dependencies"].values():
            dat[el]["used_by"].append(d["full_name"])


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


def add_categories(dat, config):
    for d in dat.values():
        name = d.get("name")
        if name in config.categories["devtool"]:
            d["type"] = "tool"
        elif name in config.categories["research"]:
            d["type"] = "research"
        else:
            d["type"] = "unknown"


def add_emojis(dat):
    for d in dat.values():
        if d.get("description_github", None) is not None:
            d["description_github"] = emoji_data_python.replace_colons(
                d["description_github"])


def write_repos(dat, config):
    if not os.path.isdir(config.data_dir):
        os.mkdir(config.data_dir)
    dest = os.path.join(config.data_dir, "repos.json")
    print(f"Writing {dest}")
    with open(dest, "w") as f:
        f.write(json.dumps(list(dat.values())))
    dest = os.path.join(config.static_dir, "repos.json")
    print(f"Writing {dest}")
    with open(dest, "w") as f:
        f.write(json.dumps(list(dat.values())))


def parse_requirements(path):
    dependencies = []
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                dependencies = \
                    [str(req) for req in pkg_resources.parse_requirements(f)]
            except:
                print(f"Failed to parse python deps at {path}")
    return dependencies
