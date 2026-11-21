"""Membuka workspace: hanya yang terdaftar di config.yaml yang bisa dijalankan."""
import shutil
import subprocess
import webbrowser

from core.config import muat_config


def buka_workspace(nama: str = "", **_) -> str:
    workspace = muat_config()["workspace"]
    nama = nama.strip().lower()
    if nama not in workspace:
        tersedia = ", ".join(workspace) or "belum ada"
        return f"Workspace '{nama}' tidak ada. Yang tersedia: {tersedia}."

    dibuka, gagal = 0, []
    for item in workspace[nama]:
        try:
            if "url" in item:
                webbrowser.open(item["url"])
            else:
                exe = shutil.which(item["program"])
                if exe is None:
                    raise FileNotFoundError(item["program"])
                subprocess.Popen([exe, *map(str, item.get("argumen", []))])
            dibuka += 1
        except Exception:
            gagal.append(str(item.get("program") or item.get("url")))

    teks = f"Workspace {nama} dibuka, {dibuka} item."
    if gagal:
        teks += f" Gagal membuka: {', '.join(gagal)}."
    return teks
