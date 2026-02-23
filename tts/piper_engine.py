import subprocess
import logging
import sounddevice as sd
import soundfile as sf
import io
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class PiperTTS:
    def __init__(self, model_path: str, length_scale: float = 1.1):
        logger.info("Initializing PiperTTS")
        self.model_path = str(Path(model_path).resolve())
        logger.debug("Resolved model path: %s", self.model_path)
        
        if not os.path.exists(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            raise FileNotFoundError(self.model_path)
        logger.info("Model file exists")

        self.length_scale = str(length_scale)
        self._piper_cmd = [
            "piper",
            "--model", self.model_path,
            "--output_file", "-",
            "--length_scale", self.length_scale,
        ]
        logger.debug("Length scale set to: %s", self.length_scale)

        logger.debug("Setting environment variables...")
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("ONNX_NUM_THREADS", "1")
        logger.info("PiperTTS initialized successfully")

    def speak(self, text: str):
        logger.debug("speak() called")
        if not text.strip():
            logger.debug("Empty text provided, skipping speech")
            return

        logger.debug("Starting piper subprocess")
        try:
            proc = subprocess.run(
                self._piper_cmd,
                input=text.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except FileNotFoundError:
            logger.error("piper binary not found")
            print("[TTS] Piper CLI not found in PATH")
            return

        wav_bytes = proc.stdout
        err = proc.stderr
        logger.debug("Piper process completed with return code: %d", proc.returncode)

        if not wav_bytes:
            logger.error("No audio produced by piper")
            print("[TTS] No audio produced")
            error_msg = err.decode(errors="ignore")
            logger.error("Piper stderr: %s", error_msg)
            print(error_msg)
            return
        logger.debug("Audio data received: %d bytes", len(wav_bytes))

        logger.debug("Decoding WAV data...")
        data, sr = sf.read(io.BytesIO(wav_bytes), dtype="float32")
        logger.debug("Audio decoded: sample_rate=%d, samples=%d", sr, data.size)

        if data.size == 0:
            logger.error("Empty audio buffer after decoding")
            print("[TTS] Empty audio buffer")
            return

        logger.debug("Playing audio...")
        sd.play(data, sr)
        sd.wait()
        logger.info("Audio playback completed")
