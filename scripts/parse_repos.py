import json
import re
import yaml
import base64
import emoji_data_python


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


def parse_r_package(api, org_name, dat):
    description = api.repos.get_content(org_name,
                                        dat["name"],
                                        "DESCRIPTION")
    desc = get_content_string(description)
    name = re.search("Package\:\s(.*)", desc)
    if name:
        dat["name"] = name.group(1)
    imports = re.search('(Imports:[^:]+)(\n(.*):)', desc)
    packages = []
    if imports:
        yml_obj = yaml.safe_load(imports.group(1))
        imports = yml_obj.get("Imports")
        if imports:
            imports = imports.split(",")
            imports = [re.sub(r"@.*|,|\s+|.*\/|\(.*\)|\r", "", p) for p in imports]
            packages = packages + imports
    remotes = re.search('(Remotes:[^:]+)(\n(.*):)', desc)
    if remotes:
        yml_obj = yaml.safe_load(remotes.group(1))
        remotes = yml_obj.get("Remotes")
        if remotes:
            remotes = remotes.split(",")
            remotes = [re.sub(r"@.*|,|\s+|.*\/|\(.*\)|\r", "", p) for p in
                       remotes]
            packages = packages + remotes

    return Repo(dat, packages)


def parse_python_package(api, org_name, dat):
    # it's not so easy to work out which packages are internal ones here
    return Repo(dat, [])


def parse_npm_package(api, org_name, dat):
    package_json = api.repos.get_content(org_name,
                                         dat["name"],
                                         "package.json")
    json_obj = json.loads(get_content_string(package_json))
    deps = json_obj.get("dependencies")
    dev_deps = json_obj.get("devDependencies")
    packages = []
    if deps:
        packages = packages + list(deps.keys())
    if dev_deps:
        packages = packages + list(dev_deps.keys())
    dat["name"] = json_obj["name"]
    return Repo(dat, packages)
