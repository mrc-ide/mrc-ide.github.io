import base64
import json
import os
import shutil

from ghapi.all import GhApi, paged

from config import Config


def fetch(root):
    config = Config(root)
    dat = fetch_all(config)
    write_data(dat, os.path.join(root, "data"))


def write_data(dat, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for k in dat.keys():
        d = dat[k]
        p = os.path.join(dest, k)
        os.makedirs(p, exist_ok = True)
        for name, content in d["metadata"].items():
            with open(os.path.join(p, name), "w") as f:
                f.write(content)
        metadata = {x: d[x] for x in d if x != "metadata"}
        with open(os.path.join(p, "metadata.json"), "w") as f:
            f.write(json.dumps(metadata))


def fetch_all(config):
    api = GhApi(token=os.environ["GITHUB_TOKEN"])
    dat = []
    for org_name in config.orgs:
        print(f"Fetching {org_name}")
        dat += fetch_org(api, org_name, config)
    print(f"Fetching extras")
    for name in config.extra:
        dat.append(fetch_single(api, name, config))
    return {x["full_name"]: x for x in dat}


def fetch_org(api, org_name, config):
    ret = []
    pages = paged(api.repos.list_for_org, per_page=100, org=org_name)
    for page in pages:
        for repo_data in page:
            try:
                dat = fetch_repo(api, org_name, repo_data, config)
                if dat:
                    ret.append(dat)
            except Exception as e:
                print(f"ERROR on {org_name}/{repo_data.name}: {str(e)}")
    return ret


def fetch_single(api, name, config):
    org_name, repo_name = name.split("/")
    repo_data = api.repos.get(org_name, repo_name)
    return fetch_repo(api, org_name, repo_data, config)


def fetch_repo(api, org_name, repo_data, config):
    repo_name = repo_data.name
    full_name = f"{org_name}/{repo_name}"
    if full_name in config.exclude:
        return
    if repo_data["archived"] or repo_data["fork"] or repo_data["private"]:
        return
    print(f"  - {full_name}")

    copy = ["created_at", "updated_at", "pushed_at",
            "stargazers_count", "homepage", "topics"]
    ret = {nm: repo_data[nm] for nm in copy}
    ret["org"] = org_name
    ret["repo"] = repo_name
    ret["full_name"] = full_name
    # We're going to overwrite this later if we can pull better data
    # from the language-specific files.
    ret["language_github"] = repo_data["language"]
    ret["description_github"] = repo_data["description"]

    branch = repo_data.default_branch
    tree = api.git.get_tree(org_name, repo_name, branch)["tree"]

    language, metadata_files = detect_language(api, org_name, repo_name,
                                               branch, config)

    ret["language"] = language
    ret["metadata"] = get_metadata(api, org_name, repo_name, metadata_files)
    ret["contributors"] = get_contributors(api, org_name, repo_name)

    return ret


def get_content_string(encoded):
    return base64.b64decode(encoded["content"]).decode("utf-8")


def detect_language(api, org_name, repo_name, branch, config):
    full_name = f"{org_name}/{repo_name}"
    tree = api.git.get_tree(org_name, repo_name, branch)["tree"]

    language = set()
    paths = [t["path"] for t in tree]
    metadata = []
    for k in config.sentinals.keys():
        if k in paths:
            language.add(config.sentinals[k])
            metadata.append(k)

    override = config.language.get(full_name, None)
    if override:
        language = set([override])

    if len(language) > 1:
        raise Exception("more than one possible langauge for {full_name}")
    if len(language) == 0:
        return (None, metadata)
    return (list(language)[0], metadata)


def get_metadata(api, org_name, repo_name, files):
    ret = {}
    for f in files:
        ret[f] = get_content_string(
            api.repos.get_content(org_name, repo_name, f))
    return ret


def get_contributors(api, org_name, repo_name):
    data = api.repos.get_contributors_stats(org_name, repo_name)
    ret = [{"user": el["author"]["login"], "count": el["total"]} for el in data]
    ret.sort(key=lambda x: x["count"], reverse=True)
    return ret
