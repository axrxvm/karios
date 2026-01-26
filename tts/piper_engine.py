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
        logger.info(f"Initializing PiperTTS with model_path: {model_path}")
        self.model_path = str(Path(model_path).resolve())
        logger.debug(f"Resolved model path: {self.model_path}")
        
        if not os.path.exists(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            raise FileNotFoundError(self.model_path)
        logger.info("Model file exists")

        self.length_scale = str(length_scale)
        logger.debug(f"Length scale set to: {length_scale}")

        logger.debug("Setting environment variables...")
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("ONNX_NUM_THREADS", "1")
        logger.info("PiperTTS initialized successfully")

    def speak(self, text: str):
        logger.debug(f"speak() called with text: {text[:50]}...")
        if not text.strip():
            logger.debug("Empty text provided, skipping speech")
            return

        logger.debug(f"Starting piper subprocess with model: {self.model_path}")
        proc = subprocess.Popen(
            [
                "piper",
                "--model", self.model_path,
                "--output_file", "-",
                "--length_scale", self.length_scale,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.debug("Piper subprocess started")

        # ---- CRITICAL SEQUENCE ----
        logger.debug("Writing text to piper stdin...")
        proc.stdin.write(text.encode("utf-8"))
        proc.stdin.flush()
        proc.stdin.close()
        logger.debug("Reading audio data from piper...")
        wav_bytes = proc.stdout.read()
        err = proc.stderr.read()
        proc.wait()
        logger.debug(f"Piper process completed with return code: {proc.returncode}")
        # --------------------------

        if not wav_bytes:
            logger.error("No audio produced by piper")
            print("[TTS] No audio produced")
            error_msg = err.decode(errors="ignore")
            logger.error(f"Piper stderr: {error_msg}")
            print(error_msg)
            return
        logger.debug(f"Audio data received: {len(wav_bytes)} bytes")

        logger.debug("Decoding WAV data...")
        data, sr = sf.read(io.BytesIO(wav_bytes), dtype="float32")
        logger.debug(f"Audio decoded: sample_rate={sr}, samples={data.size}")

        if data.size == 0:
            logger.error("Empty audio buffer after decoding")
            print("[TTS] Empty audio buffer")
            return

        logger.debug("Playing audio...")
        sd.play(data, sr)
        sd.wait()
        logger.info("Audio playback completed")
