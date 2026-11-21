"""Pencarian file (baca-saja, tidak mengubah apa pun)."""
import os

from core.config import muat_config

ABAIKAN = {".venv", ".git", "node_modules", "__pycache__", "AppData"}
BATAS_HASIL = 5


def _folder_default() -> list:
    rumah = os.path.expanduser("~")
    return [os.path.join(rumah, n) for n in ("Documents", "Downloads", "Desktop")]


def _telusuri(folders: list, kata: str, batas: int) -> list:
    hasil = []
    for folder in folders:
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in ABAIKAN]
            for nama in files:
                if kata in nama.lower():
                    hasil.append(os.path.join(root, nama))
                    if len(hasil) >= batas:
                        return hasil
    return hasil


def cari_file(kata: str = "", **_):
    kata = kata.strip().lower()
    if not kata:
        return "Sebutkan nama file yang dicari."
    folders = muat_config()["folder_pencarian"] or _folder_default()
    hasil = _telusuri(folders, kata, BATAS_HASIL)
    if not hasil:
        return f"Tidak ada file yang cocok dengan '{kata}'."
    tampil = f"Ketemu {len(hasil)} file:\n" + "\n".join(hasil)
    ucap = f"Ketemu {len(hasil)} file. Daftarnya sudah saya tampilkan di layar."
    return tampil, ucap
