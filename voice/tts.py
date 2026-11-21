"""Text-to-speech: edge-tts (online) dengan cadangan pyttsx3 (offline)."""
import asyncio
import logging
import os
import re
import tempfile
import time

from core.config import muat_config


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


def bersihkan(teks: str) -> str:
    teks = re.sub(r"\.{2,}", ".", teks)
    return re.sub(r"\s+", " ", teks).strip()


def bicara_edge(teks: str, suara: str) -> None:
    import edge_tts

    cfg = muat_config()
    path = os.path.join(tempfile.gettempdir(), "raga_suara.mp3")
    komunikasi = edge_tts.Communicate(
        teks, suara, rate=cfg["suara_laju"], pitch=cfg["suara_nada"]
    )
    asyncio.run(komunikasi.save(path))
    try:
        putar_mp3(path)
    finally:
        if os.path.exists(path):
            os.remove(path)


def bicara_offline(teks: str) -> None:
    import pyttsx3

    engine = pyttsx3.init()
    kata_kunci = muat_config()["suara_offline"].lower()
    for v in engine.getProperty("voices"):
        if kata_kunci in v.name.lower():
            engine.setProperty("voice", v.id)
            break
    engine.setProperty("rate", 165)
    engine.say(teks)
    engine.runAndWait()


def bicara(teks: str) -> None:
    teks = bersihkan(teks)
    cfg = muat_config()
    for suara in (cfg["suara_edge"], cfg["suara_cadangan"]):
        for percobaan in (1, 2):
            try:
                bicara_edge(teks, suara)
                return
            except Exception as e:
                logging.warning(
                    "edge-tts gagal (%s) | suara=%s percobaan=%d | teks=%r",
                    type(e).__name__, suara, percobaan, teks[:60],
                )
                time.sleep(percobaan)
    bicara_offline(teks)