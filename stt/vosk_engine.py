import json
import pyaudio
from vosk import Model, KaldiRecognizer
from core.config import STT_SAMPLE_RATE


class VoskSTT:
    def __init__(self, model_path: str):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, STT_SAMPLE_RATE)

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=STT_SAMPLE_RATE,
            input=True,
            frames_per_buffer=8000,
        )

        self.stream.start_stream()

    def listen(self) -> str:
        """
        Blocking listen until a full utterance is detected.
        Returns recognized text or empty string.
        """
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                return result.get("text", "").strip()

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
