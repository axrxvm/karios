import subprocess
import tempfile
import os
from pathlib import Path


class PiperTTS:
    def __init__(self, model_path: str):
        self.model_path = str(Path(model_path).resolve())

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Piper model not found: {self.model_path}")

    def speak(self, text: str):
        if not text or not text.strip():
            return

        # Create temp WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav_path = f.name

        try:
            # Run Piper (blocking)
            piper_proc = subprocess.run(
                [
                    "piper",
                    "--model", self.model_path,
                    "--output_file", wav_path,
                ],
                input=text,
                text=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=True,
            )

            # Play audio (blocking, safe)
            subprocess.run(
                [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-loglevel", "quiet",
                    wav_path,
                ],
                check=False,
            )

        except subprocess.CalledProcessError as e:
            print("[TTS] Piper failed:", e.stderr if e.stderr else e)

        finally:
            # Cleanup AFTER playback
            if os.path.exists(wav_path):
                os.remove(wav_path)
