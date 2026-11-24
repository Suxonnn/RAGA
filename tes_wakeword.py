import time

import openwakeword
import sounddevice as sd
from openwakeword.model import Model

from core.config import muat_config

KATA = "jarvis"     # potongan nama model yang dicari
AMBANG = 0.5        # 0 sampai 1; naikkan jika sering salah picu

openwakeword.utils.download_models()      # sekali saja, butuh internet
model = Model(inference_framework="onnx")

print("Ucapkan 'hey jarvis'. Ctrl+C untuk berhenti.\n")
terakhir = 0
pertama = True

with sd.InputStream(
    samplerate=16000, channels=1, dtype="int16",
    blocksize=1280, device=muat_config()["mikrofon"],
) as stream:
    while True:
        data, _ = stream.read(1280)               # 1280 sampel = 80 milidetik
        skor = model.predict(data[:, 0])
        if pertama:
            print("Model yang terbaca:", list(skor), "\n")
            pertama = False
        nilai = max(v for k, v in skor.items() if KATA in k)
        print(f"\r{nilai:.2f} {'#' * int(nilai * 40):<40}", end="", flush=True)
        if nilai > AMBANG and time.time() - terakhir > 2:
            terakhir = time.time()
            print("\n>>> TERDETEKSI")