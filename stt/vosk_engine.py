import json
import logging
from typing import Optional

import pyaudio
from vosk import Model, KaldiRecognizer
from core.config import STT_KEEP_STREAM_OPEN, STT_SAMPLE_RATE

logger = logging.getLogger(__name__)


class VoskSTT:
    def __init__(self, model_path: str):
        logger.info("Initializing VoskSTT")
        logger.debug("Loading Vosk model from %s", model_path)
        self.model = Model(model_path)
        logger.info("Vosk model loaded successfully")
        
        logger.debug("Creating KaldiRecognizer with sample rate: %d", STT_SAMPLE_RATE)
        self.recognizer = KaldiRecognizer(self.model, STT_SAMPLE_RATE)
        logger.info("KaldiRecognizer created")

        logger.debug("Initializing PyAudio...")
        self.audio = pyaudio.PyAudio()
        self.keep_stream_open = STT_KEEP_STREAM_OPEN
        self.stream: Optional[pyaudio.Stream] = None

        if self.keep_stream_open:
            self._ensure_stream()
            logger.info("VoskSTT initialized and audio stream started")
        else:
            logger.info("VoskSTT initialized in on-demand stream mode")

    def _ensure_stream(self) -> None:
        if self.stream is not None:
            return
        logger.debug("Opening audio stream...")
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=STT_SAMPLE_RATE,
            input=True,
            frames_per_buffer=8000,
        )
        logger.info("Audio stream opened")
        self.stream.start_stream()

    def _close_stream(self) -> None:
        if self.stream is None:
            return
        logger.debug("Stopping audio stream...")
        self.stream.stop_stream()
        logger.debug("Closing audio stream...")
        self.stream.close()
        self.stream = None

    def listen(self) -> str:
        """
        Blocking listen until a full utterance is detected.
        Returns recognized text or empty string.
        """
        logger.debug("listen() called - waiting for speech...")
        self._ensure_stream()
        if hasattr(self.recognizer, "Reset"):
            self.recognizer.Reset()

        iteration = 0
        try:
            while True:
                iteration += 1
                if logger.isEnabledFor(logging.DEBUG) and iteration % 100 == 0:
                    logger.debug("Still listening... (iteration %d)", iteration)
                data = self.stream.read(4000, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    logger.debug("Speech detected, processing...")
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    logger.info("Speech recognized")
                    return text
        finally:
            if not self.keep_stream_open:
                self._close_stream()

    def close(self):
        logger.info("Closing VoskSTT...")
        self._close_stream()
        logger.debug("Terminating PyAudio...")
        self.audio.terminate()
        logger.info("VoskSTT closed successfully")
