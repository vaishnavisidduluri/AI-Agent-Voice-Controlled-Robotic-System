from perception.speech.speech_recognizer import SpeechRecognizer
from perception.speech.command_parser import CommandParser


MODEL_PATH = "models/vosk-model-small-en-us-0.15"
WAKE_WORD = "hey robert"

COMMANDS = [
    "move left",
    "move right",
    "move up",
    "move down",
    "pick object",
    "drop object",
    "open gripper",
    "close gripper",
    "stop"
]


if __name__ == "__main__":

    recognizer = SpeechRecognizer(MODEL_PATH)
    parser = CommandParser(WAKE_WORD, COMMANDS)

    # 1️⃣ Listen for wake word (free speech mode)
    text = recognizer.listen("converted.wav")

    if parser.check_wake_word(text):

        # 2️⃣ Listen for restricted command
        grammar = parser.get_grammar()
        command_text = recognizer.listen("converted.wav", grammar=grammar)

        command = parser.parse_command(command_text)

        print("Final Structured Output:", command)