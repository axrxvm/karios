import json
import logging
import pyaudio
from vosk import Model, KaldiRecognizer
from core.config import STT_SAMPLE_RATE

logger = logging.getLogger(__name__)


class VoskSTT:
    def __init__(self, model_path: str):
        logger.info(f"Initializing VoskSTT with model_path: {model_path}")
        logger.debug(f"Loading Vosk model from {model_path}...")
        self.model = Model(model_path)
        logger.info("Vosk model loaded successfully")
        
        logger.debug(f"Creating KaldiRecognizer with sample rate: {STT_SAMPLE_RATE}")
        self.recognizer = KaldiRecognizer(self.model, STT_SAMPLE_RATE)
        logger.info("KaldiRecognizer created")

        logger.debug("Initializing PyAudio...")
        self.audio = pyaudio.PyAudio()
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
        logger.info("VoskSTT initialized and audio stream started")

    def listen(self) -> str:
        """
        Blocking listen until a full utterance is detected.
        Returns recognized text or empty string.
        """
        logger.debug("listen() called - waiting for speech...")
        iteration = 0
        while True:
            iteration += 1
            if iteration % 100 == 0:
                logger.debug(f"Still listening... (iteration {iteration})")
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                logger.debug("Speech detected, processing...")
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                logger.info(f"Speech recognized: {text}")
                return text

    def close(self):
        logger.info("Closing VoskSTT...")
        logger.debug("Stopping audio stream...")
        self.stream.stop_stream()
        logger.debug("Closing audio stream...")
        self.stream.close()
        logger.debug("Terminating PyAudio...")
        self.audio.terminate()
        logger.info("VoskSTT closed successfully")
