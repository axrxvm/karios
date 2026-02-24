import json
import logging
import queue

import miniaudio
from vosk import Model, KaldiRecognizer
from core.config import STT_SAMPLE_RATE

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

        self._audio_queue: queue.Queue[bytes] = queue.Queue(maxsize=64)
        self._capture_generator = self._capture_callback()
        next(self._capture_generator)

        capture_device_id = self._select_capture_device_id()
        if capture_device_id is None:
            raise RuntimeError("No input audio device available")

        self.capture_device = miniaudio.CaptureDevice(
            input_format=miniaudio.SampleFormat.SIGNED16,
            nchannels=1,
            sample_rate=STT_SAMPLE_RATE,
            device_id=capture_device_id,
        )
        self.capture_device.start(self._capture_generator)
        logger.info("VoskSTT initialized and capture stream started")

    def _select_capture_device_id(self):
        try:
            devices = miniaudio.Devices().get_captures()
            if not devices:
                return None
            default = next((d for d in devices if d.get("is_default")), None)
            return (default or devices[0]).get("id")
        except Exception:
            return None

    def _capture_callback(self):
        while True:
            data = yield
            if data is None:
                continue
            if isinstance(data, (bytes, bytearray, memoryview)):
                chunk = bytes(data)
            elif hasattr(data, "tobytes"):
                chunk = data.tobytes()
            else:
                chunk = bytes(data)

            try:
                self._audio_queue.put_nowait(chunk)
            except queue.Full:
                try:
                    self._audio_queue.get_nowait()
                except queue.Empty:
                    pass
                self._audio_queue.put_nowait(chunk)

    def listen(self) -> str:
        """
        Blocking listen until a full utterance is detected.
        Returns recognized text or empty string.
        """
        logger.debug("listen() called - waiting for speech...")
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break

        if hasattr(self.recognizer, "Reset"):
            self.recognizer.Reset()

        iteration = 0
        while True:
            iteration += 1
            if logger.isEnabledFor(logging.DEBUG) and iteration % 100 == 0:
                logger.debug("Still listening... (iteration %d)", iteration)

            data = self._audio_queue.get()
            if self.recognizer.AcceptWaveform(data):
                logger.debug("Speech detected, processing...")
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                logger.info("Speech recognized")
                return text

    def close(self):
        logger.info("Closing VoskSTT...")
        self.capture_device.stop()
        self.capture_device.close()
        logger.info("VoskSTT closed successfully")
