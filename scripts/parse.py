import json
import os

from pathlib import Path


def read_metadata(path):
    ret = {}
    for p in Path('data').rglob('metadata.json'):
        d = load_metadata(p.parent)
        key = d["full_name"]
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
        if desc["name"]:
            dat["name"] = desc["name"]
        dat["version"] = desc["version"]
        dat["title"] = desc["title"]
        dat["description"] = desc["description"]
        dat["dependencies"] = desc["dependencies"]
        dat["authors"] = desc["authors"]
    return dat


def load_metadata_python(path, dat):
    # doing this requires parsing the setup.py really
    # not sure why we failed to get any requirements.txt files though
    dat["version"] = None
    dat["title"] = None
    dat["description"] = None
    dat["dependencies"] = []
    dat["authors"] = []
    return dat


def load_metadata_js(path, dat):
    path_package = os.path.join(path, "package.json")
    if os.path.exists(path_package):
        desc = read_json(path_package)
        if desc.get("name", None):
            dat["name"] = desc["name"]
        dat["version"] = desc.get("version", None)
        dat["title"] = None
        dat["description"] = dat.get("description", None)
        dat["dependencies"] = list(dat.get("dependencies", {}).keys()) + \
            list(dat.get("devDependencies", {}).keys())
        author = dat.get("author", None)
        dat["authors"] = [author] if author else []
    return dat
