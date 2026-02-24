import subprocess
import logging
import miniaudio
import os
import re
import tempfile
import time
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
        self._output_device_id, output_name = self._select_output_device()
        if self._output_device_id is not None:
            logger.info("Using TTS output device: %s", output_name)
        else:
            logger.warning("No TTS output device detected during initialization")
        logger.info("PiperTTS initialized successfully")

    def _select_output_device(self):
        """Return (device_id, device_name) for a usable output device."""
        try:
            devices = miniaudio.Devices().get_playbacks()
            if not devices:
                return None, None
            default = next((d for d in devices if d.get("is_default")), None)
            chosen = default or devices[0]
            return chosen.get("id"), chosen.get("name")
        except Exception:
            return None, None

    def _safe_playback_stream(self, file_stream, nchannels: int):
        """
        Ensure every callback returns exactly the requested frame count.
        This prevents garbage audio from partially-unwritten output buffers.
        """
        sample_width = miniaudio.width_from_format(miniaudio.SampleFormat.SIGNED16)
        bytes_per_frame = nchannels * sample_width
        required_frames = yield b""
        while True:
            target_bytes = max(int(required_frames or 0), 0) * bytes_per_frame
            try:
                chunk = file_stream.send(required_frames)
                chunk_bytes = bytes(chunk)
            except StopIteration:
                chunk_bytes = b""

            if target_bytes > 0 and len(chunk_bytes) < target_bytes:
                chunk_bytes += b"\x00" * (target_bytes - len(chunk_bytes))
            elif target_bytes > 0 and len(chunk_bytes) > target_bytes:
                chunk_bytes = chunk_bytes[:target_bytes]

            required_frames = yield chunk_bytes

    def _play_audio(self, wav_path: str) -> bool:
        """Play audio if an output device exists."""
        device_id = self._output_device_id
        if device_id is None:
            logger.warning("No output audio device available; skipping playback")
            print("[TTS] No output audio device available; skipping playback")
            return False

        try:
            info = miniaudio.get_file_info(wav_path)
            file_stream = miniaudio.stream_file(
                wav_path,
                output_format=miniaudio.SampleFormat.SIGNED16,
                nchannels=info.nchannels,
                sample_rate=info.sample_rate,
                frames_to_read=2048,
            )
            stream = self._safe_playback_stream(file_stream, info.nchannels)
            next(stream)

            playback = miniaudio.PlaybackDevice(
                output_format=miniaudio.SampleFormat.SIGNED16,
                nchannels=info.nchannels,
                sample_rate=info.sample_rate,
                buffersize_msec=300,
                device_id=device_id,
            )
            playback.start(stream)
            # Allow full playback plus a small drain window before stopping.
            time.sleep(max(info.duration, 0.0) + 0.35)
            playback.stop()
            playback.close()
            file_stream.close()
            return True
        except Exception as exc:
            logger.error("Audio playback failed: %s", exc)
            print(f"[TTS] Audio playback failed: {exc}")
            return False

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

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name

        logger.debug("Starting piper subprocess")
        try:
            proc = subprocess.run(
                [*self._piper_cmd, "--output_file", wav_path],
                input=normalized_text.encode("utf-8"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=False,
            )
        except FileNotFoundError:
            logger.error("piper binary not found")
            print("[TTS] Piper CLI not found in PATH")
            try:
                os.remove(wav_path)
            except OSError:
                pass
            return
        try:
            err = proc.stderr

            if proc.returncode != 0:
                logger.warning("Piper failed with enhanced args. Falling back to baseline args")
                fallback_cmd = [
                    "piper",
                    "--model", self.model_path,
                    "--output_file", wav_path,
                    "--length_scale", self.length_scale,
                ]
                proc = subprocess.run(
                    fallback_cmd,
                    input=normalized_text.encode("utf-8"),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                err = proc.stderr

            logger.debug("Piper process completed with return code: %d", proc.returncode)

            if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
                logger.error("No audio produced by piper")
                print("[TTS] No audio produced")
                error_msg = err.decode(errors="ignore")
                logger.error("Piper stderr: %s", error_msg)
                print(error_msg)
                return
            logger.debug("Audio file produced: %d bytes", os.path.getsize(wav_path))

            logger.debug("Playing audio...")
            if self._play_audio(wav_path):
                logger.info("Audio playback completed")
        finally:
            try:
                os.remove(wav_path)
            except OSError:
                pass
