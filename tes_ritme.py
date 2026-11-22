import time

from core.config import muat_config
from voice import tts

TEKS = "Good evening, Master. All systems are online. Raga is ready to assist."
asli = muat_config()

# (nama, piper_laju, jeda_titik, jeda_koma)   piper_laju: kecil = cepat, besar = lambat
VARIASI = [
    ("B. jeda lebih pendek", asli["piper_laju"], 0.35, 0.15),
    ("C. laju normal, jeda pendek", 1.0, 0.35, 0.15),
    ("D. laju agak cepat, jeda sedang", 0.9, 0.45, 0.2),
]

for nama, laju, titik, koma in VARIASI:
    tts.muat_config = lambda l=laju, t=titik, k=koma: {
        **asli, "piper_laju": l, "jeda_titik_detik": t, "jeda_koma_detik": k,
    }
    print(f"{nama} | laju={laju} titik={titik} koma={koma}")
    tts.putar_wav(tts.buat_suara_piper(TEKS))
    time.sleep(1)