import wave
import winsound

from piper import PiperVoice

TEKS = "Good evening, Master. All systems are online. Raga is ready to assist."

voice = PiperVoice.load("models/en_GB-jenny_dioco-medium.onnx")
with wave.open("tes_piper.wav", "wb") as wav:
    if hasattr(voice, "synthesize_wav"):
        voice.synthesize_wav(TEKS, wav)
    else:
        voice.synthesize(TEKS, wav)

winsound.PlaySound("tes_piper.wav", winsound.SND_FILENAME)