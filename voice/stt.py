import logging
from collections import deque

import numpy as np
import sounddevice as sd

from core.config import muat_config

SAMPLE_RATE = 16000   # Whisper bekerja di 16.000 sampel per detik
BLOK = 1600           # 1600 sampel = 0,1 detik per blok
PRA_BLOK = 3          # simpan 0,3 detik sebelum suara terdeteksi

_model = None         # kosong dulu; diisi saat pertama dibutuhkan


def siapkan_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        cfg = muat_config()
        logging.info("Memuat model STT: %s", cfg["stt_model"])
        _model = WhisperModel(
            cfg["stt_model"],
            device=cfg["stt_device"],
            compute_type=cfg["stt_compute_type"],
        )
    return _model

def rekam():
    cfg = muat_config()
    ambang = cfg["ambang_hening"]
    hening_maks = int(cfg["hening_detik"] * 10)      # detik -> jumlah blok
    tunggu_maks = int(cfg["tunggu_bicara_detik"] * 10)
    total_maks = int(cfg["maks_rekam_detik"] * 10)

    pra = deque(maxlen=PRA_BLOK)   # antrean yang otomatis membuang yang paling lama
    potongan = []
    mulai = False
    blok_hening = 0
    blok_tunggu = 0

    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32",
        blocksize=BLOK, device=cfg["mikrofon"],
    ) as stream:
        for _ in range(total_maks):
            data, _overflow = stream.read(BLOK)
            blok = data[:, 0]
            keras = float(np.sqrt(np.mean(blok ** 2)))   # RMS = ukuran "volume"

            if keras >= ambang:
                if not mulai:
                    mulai = True
                    potongan.extend(pra)    # sertakan 0,3 detik sebelum bicara
                blok_hening = 0
            elif mulai:
                blok_hening += 1
            else:
                blok_tunggu += 1

            if mulai:
                potongan.append(blok)
                if blok_hening >= hening_maks:
                    break                   # sudah diam cukup lama = selesai
            else:
                pra.append(blok)
                if blok_tunggu >= tunggu_maks:
                    return None             # tidak ada yang bicara

    return np.concatenate(potongan) if potongan else None

def transkripsi(audio) -> str:
    model = siapkan_model()
    segmen, _info = model.transcribe(
        audio,
        language=muat_config()["stt_bahasa"],
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    return " ".join(s.text.strip() for s in segmen).strip()


def dengar() -> str:
    audio = rekam()
    if audio is None:
        return ""
    return transkripsi(audio)


def tes_mic(detik: int = 8) -> None:
    cfg = muat_config()
    print(f"Ambang saat ini: {cfg['ambang_hening']}. Diam sebentar, lalu bicara.\n")
    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="float32",
        blocksize=BLOK, device=cfg["mikrofon"],
    ) as stream:
        for _ in range(detik * 10):
            data, _overflow = stream.read(BLOK)
            keras = float(np.sqrt(np.mean(data[:, 0] ** 2)))
            print(f"{keras:.4f} {'#' * min(int(keras * 400), 60)}")

