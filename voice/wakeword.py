"""Wake word: mendengarkan terus-menerus dengan openWakeWord (offline dan ringan)."""
import sounddevice as sd

from core.config import muat_config

SAMPLE_RATE = 16000
BLOK = 1280   # 80 milidetik, ukuran bingkai yang diharapkan openWakeWord

_model = None


def siapkan_model():
    global _model
    if _model is None:
        import openwakeword
        from openwakeword.model import Model

        try:
            _model = Model(inference_framework="onnx")
        except Exception:
            openwakeword.utils.download_models()      # hanya jika model belum ada
            _model = Model(inference_framework="onnx")
    return _model


def tunggu_kata_pemanggil() -> None:
    """Memblokir sampai kata pemanggil terdengar. Mikrofon dilepas setelahnya."""
    cfg = muat_config()
    kata, ambang = cfg["kata_pemanggil"], cfg["ambang_pemanggil"]
    model = siapkan_model()
    if hasattr(model, "reset"):
        model.reset()                  # buang sisa audio sebelumnya

    diperiksa = False
    with sd.InputStream(
        samplerate=SAMPLE_RATE, channels=1, dtype="int16",
        blocksize=BLOK, device=cfg["mikrofon"],
    ) as stream:
        while True:
            data, _overflow = stream.read(BLOK)
            skor = model.predict(data[:, 0])
            cocok = [v for k, v in skor.items() if kata in k]
            if not diperiksa:
                if not cocok:
                    raise ValueError(f"Model '{kata}' tidak ada. Tersedia: {list(skor)}")
                diperiksa = True
            if max(cocok) >= ambang:
                return