import time
import wave

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

from core.config import muat_config

SAMPLE_RATE = 16000
DETIK = 27
JADWAL = [   # (detik ke-, kata yang diucapkan), masing-masing dua kali
    (2, "alexa"), (5, "alexa"),
    (8, "hey jarvis"), (11, "hey jarvis"),
    (14, "hey mycroft"), (17, "hey mycroft"),
    (20, "hey rhasspy"), (23, "hey rhasspy"),
]

perangkat = muat_config()["mikrofon"]
print("Siap-siap. Ucapkan kata yang tertulis TEPAT saat muncul, dengan suara normal.\n")
rekaman = sd.rec(DETIK * SAMPLE_RATE, samplerate=SAMPLE_RATE, channels=1,
                 dtype="int16", device=perangkat)
mulai = time.time()
for detik, kata in JADWAL:
    while time.time() - mulai < detik:
        time.sleep(0.05)
    print(f"[{detik:>2} dtk] ucapkan: {kata}")
sd.wait()

audio = rekaman[:, 0]
with wave.open("tes_kata.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    w.writeframes(audio.tobytes())

rms = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
print(f"\nVolume rata-rata {rms:.0f} | puncak {int(np.abs(audio).max())} dari 32767")

model = Model(inference_framework="onnx")
hasil = model.predict_clip(audio)
for kata in ("alexa", "hey_mycroft", "hey_jarvis", "hey_rhasspy"):
    nilai = [float(f.get(kata, 0.0)) for f in hasil]
    t_puncak = nilai.index(max(nilai)) * 0.08
    print(f"{kata:12} puncak {max(nilai):.2f} pada detik ke-{t_puncak:.1f}")