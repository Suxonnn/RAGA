import asyncio
import os
import tempfile

import edge_tts

from voice.tts import putar_mp3

ID = "Selamat malam. Seluruh sistem berjalan normal. Raga siap membantu."
EN = "Good evening. All systems are online. RAGA is ready to assist."

# (suara, laju, nada, kalimat)
TES = [
    ("id-ID-GadisNeural", "+0%", "+0Hz", ID),    # bawaan
    ("id-ID-GadisNeural", "-8%", "-3Hz", ID),    # lebih tenang dan dalam
    ("en-IE-EmilyNeural", "-5%", "+0Hz", EN),    # aksen Irlandia
    ("en-GB-SoniaNeural", "-5%", "+0Hz", EN),    # aksen Inggris
]

path = os.path.join(tempfile.gettempdir(), "tes_suara.mp3")
for suara, laju, nada, teks in TES:
    print(f"{suara} | laju {laju} | nada {nada}")
    asyncio.run(edge_tts.Communicate(teks, suara, rate=laju, pitch=nada).save(path))
    putar_mp3(path)