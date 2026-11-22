"""Text-to-speech: Piper (offline), suara en_GB-jenny_dioco-medium.
Cadangan terakhir: suara bawaan Windows (pyttsx3) jika Piper tidak bisa dipakai."""
import logging
import os
import re
import tempfile
import wave

from core.config import BASE_DIR, muat_config

_piper = None   # lazy loading: model dimuat saat pertama dipakai


def bersihkan(teks: str) -> str:
    return re.sub(r"\s+", " ", teks).strip()


def _muat_piper():
    global _piper
    if _piper is None:
        from piper import PiperVoice

        path = os.path.join(BASE_DIR, muat_config()["piper_model"])
        _piper = PiperVoice.load(path)
    return _piper


def buat_suara_piper(teks: str) -> str:
    """Mengubah teks menjadi file WAV (belum diputar), mengembalikan jalurnya."""
    voice = _muat_piper()
    laju = float(muat_config()["piper_laju"])
    path = os.path.join(tempfile.gettempdir(), "raga_piper.wav")
    with wave.open(path, "wb") as wav:
        try:
            from piper import SynthesisConfig
        except ImportError:
            voice.synthesize(teks, wav, length_scale=laju)      # Piper versi lama
        else:
            voice.synthesize_wav(teks, wav, syn_config=SynthesisConfig(length_scale=laju))
    return path


def putar_wav(path: str) -> None:
    import winsound

    try:
        winsound.PlaySound(path, winsound.SND_FILENAME)
    finally:
        if os.path.exists(path):
            os.remove(path)


def bicara_piper(teks: str) -> None:
    putar_wav(buat_suara_piper(teks))


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
    try:
        bicara_piper(teks)
    except Exception:
        logging.exception("Piper gagal, memakai suara bawaan Windows")
        bicara_offline(teks)