import subprocess
import logging
import sounddevice as sd
import soundfile as sf
import io
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class PiperTTS:
    def __init__(
        self,
        model_path: str,
        length_scale: float = 1.0,
        noise_scale: float = 0.667,
        noise_w: float = 0.8,
        sentence_silence: float = 0.25,
        speaker_id: int | None = None,
    ):
        logger.info("Initializing PiperTTS")
        self.model_path = str(Path(model_path).resolve())
        logger.debug("Resolved model path: %s", self.model_path)
        
        if not os.path.exists(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            raise FileNotFoundError(self.model_path)
        logger.info("Model file exists")

        self.length_scale = str(length_scale)
        self.noise_scale = str(noise_scale)
        self.noise_w = str(noise_w)
        self.sentence_silence = str(sentence_silence)

        self._piper_cmd = [
            "piper",
            "--model", self.model_path,
            "--output_file", "-",
            "--length_scale", self.length_scale,
            "--noise_scale", self.noise_scale,
            "--noise_w", self.noise_w,
            "--sentence_silence", self.sentence_silence,
        ]
        if speaker_id is not None:
            self._piper_cmd.extend(["--speaker", str(speaker_id)])

        logger.debug("Length scale set to: %s", self.length_scale)
        logger.debug(
            "Piper params: noise_scale=%s, noise_w=%s, sentence_silence=%s, speaker_id=%s",
            self.noise_scale,
            self.noise_w,
            self.sentence_silence,
            speaker_id,
        )

        logger.debug("Setting environment variables...")
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("ONNX_NUM_THREADS", "1")
        logger.info("PiperTTS initialized successfully")

    def _normalize_text(self, text: str) -> str:
        normalized = text.strip()
        if not normalized:
            return ""

        normalized = re.sub(r"https?://\S+|www\.\S+", " link ", normalized)
        normalized = re.sub(r"\S+@\S+", " email ", normalized)
        normalized = normalized.replace("&", " and ")
        normalized = normalized.replace("@", " at ")
        normalized = normalized.replace("%", " percent")
        normalized = normalized.replace("+", " plus ")
        normalized = normalized.replace("/", " slash ")
        normalized = normalized.replace("-", " ")

        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"\s+([,.;:!?])", r"\1", normalized)

        if normalized and normalized[-1] not in ".!?":
            normalized += "."
        return normalized

    def speak(self, text: str):
        logger.debug("speak() called")
        if not text.strip():
            logger.debug("Empty text provided, skipping speech")
            return

        normalized_text = self._normalize_text(text)
        if not normalized_text:
            logger.debug("Text became empty after normalization, skipping speech")
            return

        logger.debug("Starting piper subprocess")
        try:
            proc = subprocess.run(
                self._piper_cmd,
                input=normalized_text.encode("utf-8"),
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

        if proc.returncode != 0:
            logger.warning("Piper failed with enhanced args. Falling back to baseline args")
            fallback_cmd = [
                "piper",
                "--model", self.model_path,
                "--output_file", "-",
                "--length_scale", self.length_scale,
            ]
            proc = subprocess.run(
                fallback_cmd,
                input=normalized_text.encode("utf-8"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
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
