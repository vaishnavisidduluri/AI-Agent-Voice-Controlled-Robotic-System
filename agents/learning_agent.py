import json
import os


class LearningAgent:

    def __init__(self, file_path="memory.json"):
        self.file_path = file_path
        self.history = []
        self.memory = {}
        self.retry_count = 0

        # Load memory safely
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.history = data.get("history", [])
                    self.memory = data.get("memory", {})
            except:
                print("⚠️ Memory corrupted. Resetting...")
                self.history = []
                self.memory = {}

    # -----------------------------
    # SAVE MEMORY
    # -----------------------------
    def save(self):
        with open(self.file_path, "w") as f:
            json.dump({
                "history": self.history,
                "memory": self.memory
            }, f, indent=2)

    # -----------------------------
    # UPDATE SHORT MEMORY
    # -----------------------------
    def update(self, key, value):
        self.memory[key] = value
        self.save()
        print(f" Learning Agent: Updated {key}")

    # -----------------------------
    # RECORD EXPERIENCE
    # -----------------------------
    def record(self, command, result):
        self.history.append({
            "command": command,
            "result": result
        })
        self.save()

        print(f" Learning Agent: Recorded {result.upper()}")

        # Reset retry if success
        if result == "success":
            self.reset_retry()

    # -----------------------------
    # RETRY LOGIC
    # -----------------------------
    def should_retry(self):
        return self.retry_count < 2

    def increase_retry(self):
        self.retry_count += 1
        print(f" Retry Attempt: {self.retry_count}")

    def reset_retry(self):
        self.retry_count = 0
        print(" Learning Agent: Retry reset")

    # -----------------------------
    # DECISION MAKING (INTELLIGENCE)
    # -----------------------------
    def suggest_action(self):
        """
        Suggest best action based on past success
        """
        if not self.history:
            return None

        success_actions = [
            h["command"] for h in self.history if h["result"] == "success"
        ]

        if not success_actions:
            return None

        # return most recent successful action
        suggestion = success_actions[-1]

        print(" Learning Agent Suggestion:", suggestion)

        return suggestion

    # -----------------------------
    # PERFORMANCE SUMMARY
    # -----------------------------
    def summarize(self):
        total = len(self.history)

        if total == 0:
            print(" No history yet")
            return

        success = sum(1 for h in self.history if h["result"] == "success")

        print(f" Success Rate: {success}/{total}")