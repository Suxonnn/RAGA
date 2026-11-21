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
    (r"^(?:cek\s+)?ram$", "cek_ram"),
    (r"^(?:cek\s+)?cpu$", "cek_cpu"),
    (r"^(?:cek\s+)?baterai$", "cek_baterai"),
    (r"^(?:cek\s+)?disk$", "cek_disk"),
    (r"^cari(?:\s+file)?\s+(?P<kata>.+)$", "cari_file"),
    (r"^buka\s+(?P<nama>.+)$", "buka_workspace"),
]


def urai_perintah(teks: str):
    teks = teks.strip().lower()
    for pola, aksi in POLA:
        cocok = re.match(pola, teks)
        if cocok:
            return aksi, cocok.groupdict()
    return None, {}


def jalankan(aksi: str, params: dict | None = None) -> tuple[str, str]:
    """Mengembalikan (teks_untuk_layar, teks_untuk_diucapkan)."""
    fungsi = AKSI.get(aksi)
    if fungsi is None:
        pesan = "Aksi itu tidak ada dalam daftar yang diizinkan."
        return pesan, pesan
    try:
        hasil = fungsi(**(params or {}))
    except Exception:
        logging.exception("Aksi %s gagal", aksi)
        pesan = "Terjadi kesalahan saat menjalankan aksi itu."
        return pesan, pesan
    return hasil if isinstance(hasil, tuple) else (hasil, hasil)
