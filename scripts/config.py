import json
import os


class Config:
    def __init__(self, path):
        path_json = os.path.join(path, "config.json")
        with open(path_json, "r") as f:
            dat = json.load(f)
        self.exclude = dat["exclude"]
        self.extra = dat["extra"]
        self.language = dat["language"]
        self.orgs = dat["orgs"]
        self.sentinals = {
            "DESCRIPTION": "r",
            "setup.py": "python",
            "pyproject.toml": "python",
            "package.json": "js"
        }
