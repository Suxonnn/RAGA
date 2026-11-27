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
import threading

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
from voice.tts import bicara, bicara_offline, buat_suara_piper, putar_wav


def sapaan_waktu() -> str:
    jam = datetime.datetime.now().hour
    if jam < 12:
        return "morning"
    if jam < 18:
        return "afternoon"
    return "evening"

SATUAN = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
]
PULUHAN = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def angka_ke_kata(n: int) -> str:
    if n < 20:
        return SATUAN[n]
    if n < 100:
        puluh, sisa = divmod(n, 10)
        return PULUHAN[puluh] + (f" {SATUAN[sisa]}" if sisa else "")
    return "one hundred"


def susun_teks() -> str:
    
    nama = muat_config()["nama_pengguna"]
    salam = f"Good {sapaan_waktu()}" + (f", {nama}" if nama else "")
    bagian = [salam + ". All systems are online. Raga is ready to assist."]

    baterai = psutil.sensors_battery()
    if baterai:
        status = "charging" if baterai.power_plugged else "not plugged in"
        bagian.append(
            f"Battery is at {angka_ke_kata(int(baterai.percent))} percent, {status}."
        )
    bagian.append(
        f"Memory usage is at {angka_ke_kata(int(psutil.virtual_memory().percent))} percent."
    )
    return " ".join(bagian)



def desktop_siap(batas_detik: float = 60) -> bool:
    """True begitu taskbar Windows (tanda desktop sudah tampil) terdeteksi."""
    import ctypes

    mulai = time.time()
    while time.time() - mulai < batas_detik:
        if ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None):
            return True
        time.sleep(0.2)
    return False


def salam() -> None:
    cfg = muat_config()
    mulai = time.time()
    teks = susun_teks()
    logging.info("Salam: %s", teks)

    hasil = {}

    def siapkan():
        try:
            hasil["path"] = buat_suara_piper(teks)
        except Exception:
            logging.exception("Piper gagal menyiapkan suara")

    pekerja = threading.Thread(target=siapkan)
    pekerja.start()                  # bagian berat jalan di latar belakang

    desktop = desktop_siap()         # sementara itu, tunggu desktop muncul
    t_desktop = time.time()
    pekerja.join()                   # pastikan suaranya sudah jadi
    t_siap = time.time()

    sisa = cfg["jeda_setelah_desktop_detik"] - (time.time() - t_desktop)
    if sisa > 0:
        time.sleep(sisa)

    logging.info(
        "Waktu: desktop=%s pada %.1f dtk | suara siap %.1f dtk | diputar %.1f dtk",
        desktop, t_desktop - mulai, t_siap - mulai, time.time() - mulai,
    )
    if "path" in hasil:
        putar_wav(hasil["path"])
    else:
        bicara_offline(teks)


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

def mode_siaga() -> None:
    from voice.stt import dengar, siapkan_model as siapkan_stt
    from voice.wakeword import siapkan_model as siapkan_wake, tunggu_kata_pemanggil

    cfg = muat_config()
    nama = cfg["nama_pengguna"]
    sapaan = f"Yes, {nama}?" if nama else "Yes?"

    print("Memuat model (pertama kali agak lama)...")
    siapkan_wake()
    siapkan_stt()
    print(f"Siaga. Ucapkan '{cfg['kata_pemanggil']}' untuk memanggil RAGA. Ctrl+C untuk berhenti.")
    try:
        while True:
            tunggu_kata_pemanggil()
            logging.info("Kata pemanggil terdeteksi")
            print("Terdeteksi.")
            bicara(sapaan)
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
    except KeyboardInterrupt:
        print("\nRAGA berhenti.")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ketik", action="store_true")
    parser.add_argument("--suara", action="store_true")
    parser.add_argument("--siaga", action="store_true")
    parser.add_argument("--senyap", action="store_true")
    parser.add_argument("--tes-mic", action="store_true")
    args = parser.parse_args()

    if args.tes_mic:
        from voice.stt import tes_mic
        tes_mic()
    elif args.siaga:
        mode_siaga()
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
