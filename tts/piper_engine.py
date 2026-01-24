import subprocess
import sounddevice as sd
import soundfile as sf
import io
import os
from pathlib import Path


class PiperTTS:
    def __init__(self, model_path: str, length_scale: float = 1.1):
        self.model_path = str(Path(model_path).resolve())
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(self.model_path)

        self.length_scale = str(length_scale)

        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("ONNX_NUM_THREADS", "1")

    def speak(self, text: str):
        if not text.strip():
            return

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

        # ---- CRITICAL SEQUENCE ----
        proc.stdin.write(text.encode("utf-8"))
        proc.stdin.flush()
        proc.stdin.close()
        wav_bytes = proc.stdout.read()
        err = proc.stderr.read()
        proc.wait()
        # --------------------------

        if not wav_bytes:
            print("[TTS] No audio produced")
            print(err.decode(errors="ignore"))
            return

        data, sr = sf.read(io.BytesIO(wav_bytes), dtype="float32")

        if data.size == 0:
            print("[TTS] Empty audio buffer")
            return

        sd.play(data, sr)
        sd.wait()
