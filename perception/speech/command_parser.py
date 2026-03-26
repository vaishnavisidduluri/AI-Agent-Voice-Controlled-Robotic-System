import json


def parse_command(text):
    parser = CommandParser(
        "robot",
        ["move left", "move up", "move down", "move right",
         "pick up", "drop", "open gripper", "close gripper", "stop"]
    )

    # ✅ Enforce wake word
    if not parser.check_wake_word(text):
        print("Wake word not detected.")
        return None

    return parser.parse_command(text)


class CommandParser:

    def __init__(self, wake_word, commands):
        self.wake_word = wake_word.lower()
        self.commands = commands

    def check_wake_word(self, text):
        if not text:
            return False

        text = text.lower()

        if self.wake_word in text:
            print("Wake word detected!")
            return True

        return False

    def parse_command(self, text):
        if not text:
            return None

        text = text.lower()

        # ✅ Remove wake word
        if self.wake_word in text:
            text = text.replace(self.wake_word, "").strip()

        structured_output = {
            "action": None,
            "object": None,
            "destination": None,
            "confidence": 0.95
        }

        words = text.split()

        # -------------------------
        # MOVE COMMAND
        # -------------------------
        if "move" in words:
            structured_output["action"] = "move"

            if "left" in words:
                structured_output["destination"] = "left"
            elif "right" in words:
                structured_output["destination"] = "right"
            elif "up" in words:
                structured_output["destination"] = "up"
            elif "down" in words:
                structured_output["destination"] = "down"

            print("Valid command: move")
            return structured_output

        # -------------------------
        # PICK COMMAND
        # -------------------------
        elif "pick" in words or "grab" in words or "take" in words:
            structured_output["action"] = "pick"

            # ✅ Extract object (last meaningful word)
            for w in reversed(words):
                if w not in ["pick", "grab", "take", "the", "a", "an"]:
                    structured_output["object"] = w
                    break

            print("Valid command: pick")
            return structured_output

        # -------------------------
        # DROP / PLACE
        # -------------------------
        elif "drop" in words or "place" in words:
            structured_output["action"] = "drop"

            for w in reversed(words):
                if w not in ["drop", "place", "the", "a", "an"]:
                    structured_output["object"] = w
                    break

            print("Valid command: drop")
            return structured_output

        # -------------------------
        # GRIPPER
        # -------------------------
        elif "open" in words:
            structured_output["action"] = "open_gripper"
            print("Valid command: open gripper")
            return structured_output

        elif "close" in words:
            structured_output["action"] = "close_gripper"
            print("Valid command: close gripper")
            return structured_output

        # -------------------------
        # STOP
        # -------------------------
        elif "stop" in words:
            structured_output["action"] = "stop"
            print("Valid command: stop")
            return structured_output

        print("Invalid command.")
        return None

    def get_grammar(self):
        return json.dumps(self.commands)