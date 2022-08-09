import json
import os


class Config:
    def __init__(self, path):
        path_json = os.path.join(path, "config.json")
        with open(path_json, "r") as f:
            dat = json.load(f)
        self.path = path
        self.data_dir = os.path.join(path, "../data/")
        self.static_dir = os.path.join(path, "../static/")
        self.exclude = dat["exclude"]
        self.extra = dat["extra"]
        self.language = dat["language"]
        self.orgs = dat["orgs"]
        self.sentinals = {
            "DESCRIPTION": "r",
            "requirements.txt": "python",
            "setup.py": "python",
            "pyproject.toml": "python",
            "package.json": "js"
        }
        self.categories = dat["categories"]
        self.graphs = ["odin", "naomi", "individual", "orderly"]
