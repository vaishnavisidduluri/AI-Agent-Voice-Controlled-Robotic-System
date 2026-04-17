import json
import os


class LearningAgent:

    def __init__(self, file_path="memory.json"):
        self.file_path = file_path

        # --- STATE ---
        self.state = "idle"   # idle, searching, approaching, picking, holding, returning, dropping, error
        self.holding = False
        self.current_object = None
        self.last_command = None
        self.position = "home"

        # --- MEMORY ---
        self.history = []
        self.memory = {}
        self.retry_count = 0

        # Load memory
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    self.history = data.get("history", [])
                    self.memory = data.get("memory", {})
            except:
                print("⚠️ Memory corrupted. Resetting...")

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
    # STATE MANAGEMENT
    # -----------------------------
    def update_state(self, new_state):
        print(f" State: {self.state} → {new_state}")
        self.state = new_state

    # -----------------------------
    # VALIDATE COMMAND (CORE LOGIC)
    # -----------------------------
    def validate_command(self, command):
        action = command.get("action")
        obj = command.get("object")

        # Save last command
        self.last_command = command

        # --- INVALID CASES ---
        if action == "pick" and self.holding:
            return False, "Already holding an object"

        if action == "drop" and not self.holding:
            return False, "No object to drop"

        if action == "bring" and self.holding:
            return False, "Already holding something, cannot bring"

        # --- VALID ---
        self.current_object = obj
        return True, None

    # -----------------------------
    # UPDATE AFTER ACTION
    # -----------------------------
    def update_after_action(self, action, success=True):
        if not success:
            self.update_state("error")
            return

        if action == "search":
            self.update_state("searching")

        elif action == "approach":
            self.update_state("approaching")

        elif action == "pick":
            self.holding = True
            self.update_state("holding")

        elif action == "return_home":
            self.position = "home"
            self.update_state("returning")

        elif action == "drop":
            self.holding = False
            self.current_object = None
            self.update_state("idle")

    # -----------------------------
    # MEMORY UPDATE
    # -----------------------------
    def update_memory(self, key, value):
        self.memory[key] = value
        self.save()

    # -----------------------------
    # RECORD EXPERIENCE
    # -----------------------------
    def record(self, command, result):
        self.history.append({
            "command": command,
            "result": result
        })
        self.save()

        if result == "success":
            self.reset_retry()

    # -----------------------------
    # RETRY LOGIC
    # -----------------------------
    def should_retry(self):
        return self.retry_count < 2

    def increase_retry(self):
        self.retry_count += 1

    def reset_retry(self):
        self.retry_count = 0

    # -----------------------------
    # INTELLIGENT SUGGESTION
    # -----------------------------
    def suggest_action(self):
        if not self.history:
            return None

        success_actions = [
            h["command"] for h in self.history if h["result"] == "success"
        ]

        return success_actions[-1] if success_actions else None