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

KATA_KELUAR = ("keluar", "exit", "quit")

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
    if jam < 12:
        return "morning"
    if jam < 18:
        return "afternoon"
    return "evening"


def susun_teks() -> str:
    nama = muat_config()["nama_pengguna"]
    salam = f"Good {sapaan_waktu()}" + (f", {nama}" if nama else "")
    bagian = [salam + ". All systems are online. Raga is ready to assist."]

    baterai = psutil.sensors_battery()
    if baterai:
        status = "charging" if baterai.power_plugged else "not plugged in"
        bagian.append(f"Battery is at {int(baterai.percent)} percent, {status}.")
    bagian.append(f"Memory usage is at {int(psutil.virtual_memory().percent)} percent.")
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
        if teks.lower() in KATA_KELUAR:
            break
        proses_perintah(teks, bersuara)

def proses_perintah(teks: str, bersuara: bool) -> None:
    aksi, params = urai_perintah(teks)
    if aksi is None:
        tampil = ucap = "Sorry, I don't understand that command yet."
    else:
        tampil, ucap = jalankan(aksi, params)
    print(tampil)
    if bersuara:
        bicara(ucap)

def mode_suara() -> None:
    from voice.stt import dengar, siapkan_model

    print("Memuat model suara (pertama kali akan mengunduh, mohon tunggu)...")
    siapkan_model()
    print("Siap. Tekan Enter, lalu bicara. Ketik 'keluar' untuk berhenti.")
    while True:
        try:
            masukan = input("[Enter] > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break
        if masukan in KATA_KELUAR:
            break
        print("Mendengarkan...")
        try:
            teks = dengar()
        except Exception as e:
            logging.exception("Gagal mendengar")
            print(f"Mikrofon bermasalah: {e}")
            continue
        if not teks:
            print("(tidak ada suara terdengar)")
            continue
        print(f"Kamu: {teks}")
        proses_perintah(teks, bersuara=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ketik", action="store_true")
    parser.add_argument("--suara", action="store_true")
    parser.add_argument("--senyap", action="store_true")
    parser.add_argument("--tes-mic", action="store_true")
    args = parser.parse_args()

    if args.tes_mic:
        from voice.stt import tes_mic
        tes_mic()
    elif args.suara:
        mode_suara()
    elif args.ketik:
        mode_ketik(bersuara=not args.senyap)
    else:
        salam()



if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("RAGA error")
        raise
