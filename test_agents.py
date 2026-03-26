from perception.speech.command_parser import CommandParser

WAKE_WORD = "hey robot"

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

parser = CommandParser(WAKE_WORD, COMMANDS)

# -----------------------------
# Simulated Inputs
# -----------------------------

fake_inputs = [
    "hey robot move left",
    "hey robot open gripper",
    "move right",
    "random speech"
]


for text in fake_inputs:
    print("\nInput:", text)

    if parser.check_wake_word(text):
        print("Wake word OK")

    command = parser.parse_command(text)
    if command:
        print("Command OK:", command)