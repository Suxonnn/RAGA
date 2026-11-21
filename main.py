"""RAGA.

python main.py                  -> salam otomatis (dipakai Task Scheduler)
python main.py --ketik          -> mode perintah lewat ketikan
python main.py --ketik --senyap -> mode ketikan tanpa suara
"""
import argparse
import datetime
import logging
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename=os.path.join(BASE_DIR, "raga.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

import psutil  # noqa: E402

from core.config import muat_config  # noqa: E402
from core.router import jalankan, urai_perintah  # noqa: E402
from voice.tts import bicara  # noqa: E402


def sapaan_waktu() -> str:
    jam = datetime.datetime.now().hour
    if jam < 11:
        return "pagi"
    if jam < 15:
        return "siang"
    if jam < 19:
        return "sore"
    return "malam"


def susun_teks() -> str:
    nama = muat_config()["nama_pengguna"]
    salam = f"Selamat {sapaan_waktu()}" + (f", {nama}" if nama else "")
    bagian = [salam + ". Raga siap membantu."]

    baterai = psutil.sensors_battery()
    if baterai:
        status = "sedang diisi" if baterai.power_plugged else "belum dicolok"
        bagian.append(f"Baterai tersisa {int(baterai.percent)} persen, {status}.")
    bagian.append(f"Pemakaian RAM saat ini {int(psutil.virtual_memory().percent)} persen.")
    return " ".join(bagian)


def salam() -> None:
    time.sleep(muat_config()["jeda_awal_detik"])
    teks = susun_teks()
    logging.info("Salam: %s", teks)
    bicara(teks)


def mode_ketik(bersuara: bool) -> None:
    print("RAGA siap. Contoh: cek ram | cek baterai | cari file laporan | buka coding")
    print("Ketik 'keluar' untuk berhenti.")
    while True:
        try:
            teks = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not teks:
            continue
        if teks.lower() in ("keluar", "exit", "quit"):
            break
        aksi, params = urai_perintah(teks)
        if aksi is None:
            tampil = ucap = "Maaf, aku belum mengerti perintah itu."
        else:
            tampil, ucap = jalankan(aksi, params)
        print(tampil)
        if bersuara:
            bicara(ucap)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ketik", action="store_true")
    parser.add_argument("--senyap", action="store_true")
    args = parser.parse_args()
    if args.ketik:
        mode_ketik(bersuara=not args.senyap)
    else:
        salam()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("RAGA error")
        raise
