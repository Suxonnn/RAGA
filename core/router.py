"""Router perintah. AKSI adalah whitelist: hanya fungsi di sini yang bisa dijalankan.

Nanti, LLM cukup menghasilkan pasangan (aksi, params) yang sama seperti
urai_perintah() di bawah, lalu diteruskan ke jalankan().
"""
import logging
import re

from actions import aplikasi, berkas, sistem

AKSI = {
    "cek_ram": sistem.cek_ram,
    "cek_cpu": sistem.cek_cpu,
    "cek_baterai": sistem.cek_baterai,
    "cek_disk": sistem.cek_disk,
    "cari_file": berkas.cari_file,
    "buka_workspace": aplikasi.buka_workspace,
}

POLA = [
    (r"^(?:cek\s+|check\s+)?ram$", "cek_ram"),
    (r"^(?:cek\s+|check\s+)?cpu$", "cek_cpu"),
    (r"^(?:cek\s+|check\s+)?(?:baterai|battery)$", "cek_baterai"),
    (r"^(?:cek\s+|check\s+)?(?:disk|storage)$", "cek_disk"),
    (r"^(?:cari|find|search)(?:\s+(?:file|for))?\s+(?P<kata>.+)$", "cari_file"),
    (r"^(?:buka|open)\s+(?P<nama>.+)$", "buka_workspace"),
]

def normalisasi(teks: str) -> str:
    teks = re.sub(r"[,!?;]", " ", teks.lower())
    teks = re.sub(r"\s+", " ", teks).strip(" .")
    return re.sub(r"^((?:raga|tolong|coba|please)\s+)+", "", teks)


def urai_perintah(teks: str):
    teks = normalisasi(teks)          
    for pola, aksi in POLA:
        cocok = re.match(pola, teks)
        if cocok:
            return aksi, cocok.groupdict()
    return None, {}


def jalankan(aksi: str, params: dict | None = None) -> tuple[str, str]:
    """Mengembalikan (teks_untuk_layar, teks_untuk_diucapkan)."""
    fungsi = AKSI.get(aksi)
    if fungsi is None:
        pesan = "That action is not on the allowed list."
        return pesan, pesan
    try:
        hasil = fungsi(**(params or {}))
    except Exception:
        logging.exception("Aksi %s gagal", aksi)
        pesan = "Something went wrong while running that action."
        return pesan, pesan
    return hasil if isinstance(hasil, tuple) else (hasil, hasil)
