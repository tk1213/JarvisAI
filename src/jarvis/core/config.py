from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[3]


class Config:

    def __init__(self):

        path = BASE_DIR / "config" / "settings.yaml"

        with open(path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def get(self, *keys):

        value = self.data

        for k in keys:
            value = value[k]

        return value


config = Config()