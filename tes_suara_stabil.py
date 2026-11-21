import asyncio
import os
import tempfile
import time

import edge_tts

SUARA = ["en-IE-EmilyNeural", "en-GB-SoniaNeural", "id-ID-GadisNeural"]
EN = "Good evening, Master. All systems are online."
ID = "Selamat malam. Semua sistem berjalan normal."

path = os.path.join(tempfile.gettempdir(), "stabil.mp3")
hasil = {s: 0 for s in SUARA}

for putaran in range(6):
    for s in SUARA:
        teks = ID if s.startswith("id") else EN
        try:
            asyncio.run(edge_tts.Communicate(teks, s).save(path))
            hasil[s] += 1
        except Exception:
            pass
        time.sleep(2)

for s, n in hasil.items():
    print(f"{s}: {n} dari 6 berhasil")