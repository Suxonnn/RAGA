"""Text-to-speech: edge-tts (online) dengan cadangan pyttsx3 (offline)."""
import asyncio
import logging
import os
import tempfile

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


def bicara_edge(teks: str) -> None:
    import edge_tts

    path = os.path.join(tempfile.gettempdir(), "raga_suara.mp3")
    asyncio.run(edge_tts.Communicate(teks, muat_config()["suara_edge"]).save(path))
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
