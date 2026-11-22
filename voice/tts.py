"""Text-to-speech: Piper (offline), suara en_GB-jenny_dioco-medium.
Cadangan terakhir: suara bawaan Windows (pyttsx3) jika Piper tidak bisa dipakai."""
import logging
import os
import re
import tempfile
import wave
import io

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
    """Mengubah teks menjadi satu file WAV, dengan jeda di tanda baca."""
    cfg = muat_config()
    daftar = _pecah(teks)
    if not daftar:
        raise ValueError("teks kosong")

    voice = _muat_piper()
    laju = float(cfg["piper_laju"])
    path = os.path.join(tempfile.gettempdir(), "raga_piper.wav")

    with wave.open(path, "wb") as keluar:
        diatur = False
        for potongan, jeda in daftar:
            with wave.open(_sintesis(voice, potongan, laju), "rb") as masuk:
                if not diatur:
                    keluar.setparams(masuk.getparams())
                    diatur = True
                keluar.writeframes(masuk.readframes(masuk.getnframes()))
                lebar = masuk.getsampwidth() * masuk.getnchannels()
                kecepatan = masuk.getframerate()
            keluar.writeframes(b"\x00" * int(kecepatan * jeda) * lebar)
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

def _pecah(teks: str) -> list:
    """Memecah teks per kalimat/klausa, tiap potong disertai lama jeda sesudahnya."""
    cfg = muat_config()
    hasil = []
    for p in re.findall(r"[^.,!?;:]+[.,!?;:]?", teks):
        p = p.strip()
        isi = p.rstrip(".,!?;:").strip()
        if not isi:
            continue
        if p[-1] in ".!?":
            jeda = cfg["jeda_titik_detik"]
        elif p[-1] in ",;:":
            jeda = cfg["jeda_koma_detik"]
        else:
            jeda = 0.0
        hasil.append((p, jeda))
    return hasil


def _sintesis(voice, teks: str, laju: float) -> io.BytesIO:
    """Menyintesis satu potongan teks ke WAV di memori (tanpa menyentuh disk)."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        try:
            from piper import SynthesisConfig
        except ImportError:
            voice.synthesize(teks, wav, length_scale=laju)      # Piper versi lama
        else:
            voice.synthesize_wav(teks, wav, syn_config=SynthesisConfig(length_scale=laju))
    buf.seek(0)
    return buf