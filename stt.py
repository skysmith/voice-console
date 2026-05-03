from faster_whisper import WhisperModel

_model_cache: dict[str, WhisperModel] = {}


def _get_model(model_name: str) -> WhisperModel:
    if model_name not in _model_cache:
        # int8 is the most compatible + usually fast on cpu
        _model_cache[model_name] = WhisperModel(
            model_name,
            device="cpu",
            compute_type="int8",
        )
    return _model_cache[model_name]


def transcribe_audio(samples, model_name: str = "tiny.en") -> str:
    if samples is None or getattr(samples, "size", 0) == 0:
        return ""

    model = _get_model(model_name)
    segments, _info = model.transcribe(
        samples,
        language="en",
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 250},
        beam_size=1,
        best_of=1,
    )
    return "".join(seg.text for seg in segments).strip()