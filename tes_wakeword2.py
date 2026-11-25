import numpy as np
import sounddevice as sd
from openwakeword.model import Model

from core.config import muat_config

GAIN = 4.0      # naikkan (misalnya 5.0) kalau volume mikrofon terlalu kecil
KANDIDAT = ("alexa", "hey_mycroft", "hey_jarvis", "hey_rhasspy")

model = Model(inference_framework="onnx")
perangkat = muat_config()["mikrofon"]
info = sd.query_devices(perangkat, "input")
print("Mikrofon:", info["name"])
print("Ucapkan bergantian: hey jarvis, alexa, hey mycroft. Ctrl+C untuk berhenti.\n")

puncak = {k: 0.0 for k in KANDIDAT}     # skor tertinggi sejak tes dimulai

with sd.InputStream(
    samplerate=16000, channels=1, dtype="int16",
    blocksize=1280, device=perangkat,
) as stream:
    while True:
        data, _ = stream.read(1280)
        audio = data[:, 0]
        if GAIN != 1.0:
            audio = np.clip(audio.astype(np.float32) * GAIN, -32768, 32767).astype(np.int16)

        volume = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
        skor = model.predict(audio)
        for k in KANDIDAT:
            puncak[k] = max(puncak[k], float(skor.get(k, 0.0)))

        teks = " ".join(f"{k.replace('hey_', '')}={puncak[k]:.2f}" for k in KANDIDAT)
        print(f"\rvol {volume:6.0f} | {teks}   ", end="", flush=True)