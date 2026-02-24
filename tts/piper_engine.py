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
        speaker_id: int | None = None,
    ):
        logger.info("Initializing PiperTTS")
        self.model_path = str(Path(model_path).resolve())
        logger.debug("Resolved model path: %s", self.model_path)
        
        if not os.path.exists(self.model_path):
            logger.error(f"Model file not found: {self.model_path}")
            raise FileNotFoundError(self.model_path)
        logger.info("Model file exists")

        self._piper_cmd = [
            "piper",
            "--model", self.model_path,
        ]
        if speaker_id is not None:
            self._piper_cmd.extend(["--speaker", str(speaker_id)])

        logger.debug("Piper speaker_id=%s", speaker_id)

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

            if len(devices) == 1:
                only = devices[0]
                return only.get("id"), only.get("name")

            default_index = next(
                (index for index, device in enumerate(devices, start=1) if device.get("is_default")),
                1,
            )

            print("[TTS] Multiple audio output devices detected:")
            for index, device in enumerate(devices, start=1):
                name = device.get("name", "Unknown Device")
                suffix = " (default)" if index == default_index else ""
                print(f"  {index}. {name}{suffix}")

            try:
                selection = input(
                    f"[TTS] Select output device [1-{len(devices)}] (default {default_index}): "
                ).strip()
            except EOFError:
                selection = ""

            if not selection:
                chosen_index = default_index
            else:
                try:
                    chosen_index = int(selection)
                except ValueError:
                    print(f"[TTS] Invalid selection '{selection}'. Using default {default_index}.")
                    chosen_index = default_index
                else:
                    if not 1 <= chosen_index <= len(devices):
                        print(f"[TTS] Selection out of range. Using default {default_index}.")
                        chosen_index = default_index

            chosen = devices[chosen_index - 1]
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
                logger.warning("Piper failed. Falling back to baseline args")
                fallback_cmd = [
                    "piper",
                    "--model", self.model_path,
                    "--output_file", wav_path,
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
