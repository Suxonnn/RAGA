import os

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT = {
    "nama_pengguna": "",
    "piper_model": "models/en_GB-jenny_dioco-medium.onnx",
    "piper_laju": 1.2,
    "suara_offline": "Zira",
    "jeda_setelah_desktop_detik": 2,
    "folder_pencarian": [],
    "workspace": {},
    "stt_model": "small",
    "stt_device": "cpu",
    "stt_compute_type": "int8",
    "stt_bahasa": "id",
    "mikrofon": None,
    "ambang_hening": 0.01,
    "hening_detik": 1.2,
    "tunggu_bicara_detik": 6,
    "maks_rekam_detik": 15,
    "jeda_titik_detik": 0.6,
    "jeda_koma_detik": 0.25,
}


def muat_config() -> dict:
    data = {}
    try:
        with open(os.path.join(BASE_DIR, "config.yaml"), encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        pass
    return {**DEFAULT, **data}
