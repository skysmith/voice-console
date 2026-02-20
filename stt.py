import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


_model_cache: dict[str, WhisperModel] = {}


def _get_model(model_name: str) -> WhisperModel:
    # cpu-only default. if you have metal/cuda stuff later, we can tune compute_type.
    if model_name not in _model_cache:
        _model_cache[model_name] = WhisperModel(model_name, device="cpu", compute_type="int8")
    return _model_cache[model_name]


def transcribe_from_mic(seconds: float = 4.0, model_name: str = "small", sample_rate: int = 16000) -> str:
    print("recording…")
    audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    print("transcribing…")

    # flatten to 1d float32
    samples = np.squeeze(audio).astype(np.float32)

    model = _get_model(model_name)
    segments, _info = model.transcribe(samples, language="en")

    text = "".join(seg.text for seg in segments).strip()
    return text