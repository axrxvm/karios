import logging
from uuid import uuid4
from core.router import route
from stt.vosk_engine import VoskSTT
from tts.piper_engine import PiperTTS
from core.state import STATE
from core.config import (
    LOG_LEVEL,
    VOSK_MODEL_PATH,
    PIPER_MODEL_PATH,
    PIPER_LENGTH_SCALE,
    PIPER_NOISE_SCALE,
    PIPER_NOISE_W,
    PIPER_SENTENCE_SILENCE,
    PIPER_SPEAKER_ID,
)


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='karios.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

EXIT_WORDS = {"exit", ":q", "quit"}

logger.debug(f"VOSK_MODEL_PATH set to: {VOSK_MODEL_PATH}")
logger.debug(f"PIPER_MODEL_PATH set to: {PIPER_MODEL_PATH}")


def get_input(stt: VoskSTT) -> str:
    """
    Press Enter to type.
    Speak otherwise.
    """
    logger.debug("get_input() called")
    try:
        typed = input("You (press Enter to speak, or type): ").strip()
        if typed:
            logger.debug(f"User typed input: {typed}")
            return typed
    except EOFError:
        logger.debug("EOFError caught, returning empty string")
        return ""

    print("Listening...")
    logger.debug("Listening for voice input...")
    result = stt.listen() or ""
    logger.debug(f"Voice input received: {result}")
    return result


def main():
    logger.info("=" * 50)
    logger.info("Karios starting...")
    logger.info("=" * 50)
    print("Karios starting...")

    logger.debug("Initializing VoskSTT...")
    stt = VoskSTT(VOSK_MODEL_PATH)
    logger.info("VoskSTT initialized successfully")
    
    logger.debug("Initializing PiperTTS...")
    tts = PiperTTS(
        PIPER_MODEL_PATH,
        length_scale=PIPER_LENGTH_SCALE,
        noise_scale=PIPER_NOISE_SCALE,
        noise_w=PIPER_NOISE_W,
        sentence_silence=PIPER_SENTENCE_SILENCE,
        speaker_id=PIPER_SPEAKER_ID,
    )
    logger.info("PiperTTS initialized successfully")

    logger.debug("Speaking initial greeting")
    tts.speak("Hi, how can I help you today?")
    session_id = str(uuid4())
    logger.info("Session started: %s", session_id)

    try:
        logger.info("Entering main loop")
        while True:
            logger.debug("Waiting for user input...")
            text = get_input(stt)

            if not text:
                logger.debug("Empty input received, continuing loop")
                continue

            if text.lower() in EXIT_WORDS:
                logger.info("Exit command received")
                break

            print(f"You: {text}")
            logger.info("User input received")
            STATE.last_user_text = text
            logger.debug("Updated STATE.last_user_text")

            logger.debug("Routing user input...")
            result = route(text, session_id=session_id)
            logger.debug("Route result - handled_locally: %s", result.handled_locally)

            if result.handled_locally and result.action:
                logger.debug("Executing local action")
                response = result.action(result.arg)
                logger.debug("Local action response ready")
            else:
                logger.debug("Using LLM response")
                response = result.text

            STATE.last_response = response
            logger.debug("Updated STATE.last_response")
            print(f"Karios: {response}")
            logger.info("Karios response sent")

            logger.debug("Speaking response...")
            tts.speak(response)
            logger.debug("Response spoken successfully")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
        pass

    finally:
        logger.info("Shutting down Karios...")
        tts.speak("Shutting down. Goodbye.")
        print("Shutting down Karios.")
        logger.debug("Closing STT engine...")
        stt.close()
        logger.info("Karios shutdown complete")


if __name__ == "__main__":
    main()
