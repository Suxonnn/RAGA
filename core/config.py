import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT = {
    "nama_pengguna": "",
    "suara_edge": "id-ID-GadisNeural",
    "jeda_awal_detik": 5,
    "folder_pencarian": [],
    "workspace": {},
}


def muat_config() -> dict:
    data = {}
    try:
        with open(os.path.join(BASE_DIR, "config.yaml"), encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        pass
    return {**DEFAULT, **data}
