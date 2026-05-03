import threading
import numpy as np
import sounddevice as sd

class PushToTalkRecorder:
    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._frames = []
        self._lock = threading.Lock()
        self._stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            pass
        with self._lock:
            self._frames.append(indata.copy())

    def start(self):
        with self._lock:
            self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            if not self._frames:
                return np.array([], dtype=np.float32)
            audio = np.concatenate(self._frames, axis=0)
        return np.squeeze(audio).astype(np.float32)