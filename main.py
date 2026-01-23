from core.router import route
from stt.vosk_engine import VoskSTT
from tts.piper_engine import PiperTTS
from core.state import STATE


VOSK_MODEL_PATH = "models/vosk"
PIPER_MODEL_PATH = "models/piper/en_US-ryan-medium.onnx"


def get_input(stt: VoskSTT) -> str:
    """
    Press Enter to type.
    Speak otherwise.
    """
    try:
        typed = input("You (press Enter to speak, or type): ").strip()
        if typed:
            return typed
    except EOFError:
        return ""

    print("Listening...")
    return stt.listen() or ""


def main():
    print("Karios starting...")

    stt = VoskSTT(VOSK_MODEL_PATH)
    tts = PiperTTS(PIPER_MODEL_PATH)

    tts.speak("Hello Sir, how may I help you?")

    try:
        while True:
            text = get_input(stt)

            if not text:
                continue

            if text.lower() in {"exit", ":q", "quit"}:
                break

            print(f"You: {text}")
            STATE.last_user_text = text

            result = route(text)

            if result.handled_locally and result.action:
                response = result.action(result.arg)
            else:
                response = result.text

            STATE.last_response = response
            print(f"Karios: {response}")

            tts.speak(response)

    except KeyboardInterrupt:
        pass

    finally:
        tts.speak("Shutting down. Goodbye.")
        print("Shutting down Karios.")
        stt.close()


if __name__ == "__main__":
    main()
