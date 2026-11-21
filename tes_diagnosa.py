import asyncio
import os
import tempfile

import edge_tts

from core.config import muat_config
from main import susun_teks

cfg = muat_config()
teks = susun_teks()
path = os.path.join(tempfile.gettempdir(), "diagnosa.mp3")
suara, laju, nada = cfg["suara_edge"], cfg["suara_laju"], cfg["suara_nada"]


def coba(nama, t, s=suara, l=laju, n=nada):
    try:
        asyncio.run(edge_tts.Communicate(t, s, rate=l, pitch=n).save(path))
        print("BERHASIL:", nama)
    except Exception as e:
        print("GAGAL   :", nama, "->", type(e).__name__)


print("Teks:", teks, "\n")

for i in range(1, 4):
    coba(f"A{i}. teks penuh, ulangan {i}", teks)

coba("B. tanpa kata Raga", teks.replace("Raga is ready to assist.", "I am ready to assist."))
coba("C. Raga dieja Rah-ga", teks.replace("Raga", "Rah-ga"))
coba("D. tanpa koma", teks.replace(",", ""))

for i, kalimat in enumerate(teks.split(". "), 1):
    coba(f"E{i}. {kalimat[:35]}", kalimat)