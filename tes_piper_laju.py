import time
import wave
import winsound

from piper import PiperVoice

try:
    from piper import SynthesisConfig
except ImportError:
    SynthesisConfig = None          # versi Piper lama

TEKS = "Good evening, Master. All systems are online. Raga is ready to assist."
voice = PiperVoice.load("models/en_GB-jenny_dioco-medium.onnx")


def sintesis(teks, wav, laju):
    if SynthesisConfig is not None and hasattr(voice, "synthesize_wav"):
        voice.synthesize_wav(teks, wav, syn_config=SynthesisConfig(length_scale=laju))
    else:
        voice.synthesize(teks, wav, length_scale=laju)


for laju in (1.0, 1.2, 1.4, 1.6):
    print("length_scale =", laju)
    with wave.open("tes_laju.wav", "wb") as wav:
        sintesis(TEKS, wav, laju)
    winsound.PlaySound("tes_laju.wav", winsound.SND_FILENAME)
    time.sleep(1)