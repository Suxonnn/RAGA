"""RAGA - Tahap 1: salam otomatis setelah login Windows."""
import asyncio
import datetime
import logging
import os
import tempfile
import time

import psutil

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    filename=os.path.join(BASE_DIR, "raga.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

NAMA_PENGGUNA = "Marian Marxrist"  # isi namamu, misalnya "Budi"; kosongkan jika tidak perlu
SUARA_EDGE = "id-ID-GadisNeural"  # alternatif: "id-ID-ArdiNeural" (pria)
JEDA_AWAL_DETIK = 3  # beri waktu desktop & Wi-Fi siap


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
    bagian = [f"Selamat {sapaan_waktu()}"]
    if NAMA_PENGGUNA:
        bagian[0] += f", {NAMA_PENGGUNA}"
    bagian[0] += ". Raga siap membantu."

    baterai = psutil.sensors_battery()
    if baterai:
        status = "sedang diisi" if baterai.power_plugged else "belum dicolok"
        bagian.append(f"Baterai tersisa {int(baterai.percent)} persen, {status}.")

    ram = psutil.virtual_memory().percent
    bagian.append(f"Pemakaian RAM saat ini {int(ram)} persen.")
    return " ".join(bagian)


def putar_mp3(path: str) -> None:
    import ctypes

    mci = ctypes.windll.winmm.mciSendStringW
    mci("close raga", None, 0, 0)
    if mci(f'open "{path}" type mpegvideo alias raga', None, 0, 0) != 0:
        raise RuntimeError("MCI gagal membuka file audio")
    try:
        mci("play raga wait", None, 0, 0)
    finally:
        mci("close raga", None, 0, 0)


def bicara_edge(teks: str) -> None:
    import edge_tts

    path = os.path.join(tempfile.gettempdir(), "raga_salam.mp3")
    asyncio.run(edge_tts.Communicate(teks, SUARA_EDGE).save(path))
    try:
        putar_mp3(path)
    finally:
        if os.path.exists(path):
            os.remove(path)


def bicara_offline(teks: str) -> None:
    import pyttsx3

    engine = pyttsx3.init()
    engine.setProperty("rate", 165)
    engine.say(teks)
    engine.runAndWait()


def bicara(teks: str) -> None:
    try:
        bicara_edge(teks)
    except Exception as e:
        logging.warning("edge-tts gagal (%s), pakai suara offline", e)
        bicara_offline(teks)


def main() -> None:
    time.sleep(JEDA_AWAL_DETIK)
    teks = susun_teks()
    logging.info("Salam: %s", teks)
    bicara(teks)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("RAGA error")