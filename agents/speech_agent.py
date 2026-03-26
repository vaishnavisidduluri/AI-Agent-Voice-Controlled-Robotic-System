from perception.speech.speech_recognizer import SpeechRecognizer
from perception.speech.command_parser import parse_command

# ✅ CONFIG
USE_TEXT_INPUT = True   # use keyboard input
USE_MIC = False         # use microphone (set True when ready)

# create recognizer only once
recognizer = SpeechRecognizer("models/vosk-model-small-en-us-0.15")


class SpeechAgent:

    def __init__(self):
        self.last_text = None

    def get_command(self):
        try:
            # -----------------------------
            # INPUT SOURCE
            # -----------------------------
            if USE_TEXT_INPUT:
                text = input("🎤 Say command: ")

            else:
                if USE_MIC:
                    text = recognizer.listen_from_mic()
                else:
                    text = recognizer.listen("temp.wav")

            # -----------------------------
            # VALIDATION
            # -----------------------------
            if not text or text == self.last_text:
                return {"status": "no_input"}

            self.last_text = text

            # -----------------------------
            # PARSE COMMAND
            # -----------------------------
            command = parse_command(text)

            if not command:
                return {"status": "invalid"}

            # -----------------------------
            # SUCCESS
            # -----------------------------
            return {
                "status": "ok",
                "command": command
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }