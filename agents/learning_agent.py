class LearningAgent:

    def __init__(self):
        self.history = []

    def record(self, command, result):
        entry = {
            "command": command,
            "result": result
        }
        self.history.append(entry)

        print("📚 Learning Agent: Recorded experience")

    def summarize(self):
        total = len(self.history)

        if total == 0:
            print("📊 Learning Agent: No data yet")
            return

        success = sum(1 for h in self.history if h["result"] == "success")

        print(f"📊 Learning Agent: {success}/{total} successful tasks")