import time
from agents.speech_agent import SpeechAgent
from agents.vision_agent import VisionAgent
from agents.learning_agent import LearningAgent
from agents.motor_control_agent import MotorControlAgent
from planner.task_planner import TaskPlanner
from utils.logger import log

import yaml

# 🔁 Use this for simulation

USE_SIMULATION = True

if USE_SIMULATION:
    from simulation.mock_servo import MockServo as ServoController
else:
    from hardware.servo_controller import ServoController



with open("config/agent_settings.yaml") as f:
    settings = yaml.safe_load(f)

# 🔌 For real hardware (later)
# from hardware.servo_controller import ServoController


class MasterAgent:

    def __init__(self):
        self.speech = SpeechAgent()
        self.vision = VisionAgent()
        self.context = LearningAgent()
        self.safety = MotorControlAgent()
        self.planner = TaskPlanner()
        self.servo = ServoController()

    def run(self):
        print("🚀 Agentic System Started...\n")

        while True:
            self.process_cycle()
            time.sleep(1)  # prevent overload

    def process_cycle(self):

        print("\n🔄 New Cycle Started")

        # -----------------------------
        # 1️⃣ SPEECH AGENT
        # -----------------------------
        speech_out = self.speech.get_command()

        if speech_out["status"] == "no_input":
           
            log("🎤 Speech Agent: Waiting for input")
            return

        if speech_out["status"] == "invalid":
            print("🎤 Speech Agent: ⚠️ Invalid command")
            return

        if speech_out["status"] == "error":
            print("🎤 Speech Agent: ❌ Error")
            return

        print("🎤 Speech Agent: ✅ Working")

        command = speech_out["command"]
        print("➡️ Command:", command)

        # -----------------------------
        # 2️⃣ VISION AGENT
        # -----------------------------
        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":
            print("👁️ Vision Agent: ❌ No object detected")
            return

        print("👁️ Vision Agent: ✅ Working")

        detections = vision_out["detections"]
        print("➡️ Detections:", detections)

        # -----------------------------
        # 3️⃣ PLANNER AGENT
        # -----------------------------
        plan = self.planner.plan_task(command, detections)

        if plan["status"] != "ok":
            print("🧠 Planner Agent: ❌ Failed")
            return

        print("🧠 Planner Agent: ✅ Working")

        steps = plan["steps"]
        print("➡️ Plan:", steps)

        # -----------------------------
        # 4️⃣ SAFETY AGENT
        # -----------------------------
        safety = self.safety.validate(steps)

        if not safety["safe"]:
            print("🛡️ motor control Agent: ❌ Unsafe →", safety["reason"])
            return

        print("🛡️ motor control Agent: ✅ Safe")

        # -----------------------------
        # 5️⃣ EXECUTION
        # -----------------------------
        print("⚙️ Execution Agent: ✅ Running")

        for step in steps:
            if "servo_id" in step:
                self.servo.move(step["servo_id"], step["angle"])

            elif "gripper" in step:
                self.servo.control_gripper(step["gripper"])

            time.sleep(step.get("delay", 0.5))

        print("⚙️ Execution Agent: ✅ Completed")
        # -----------------------------
        # 6️⃣ LEARNING AGENT
        # -----------------------------
        success = self.check_task_success()

        if success:
            print("🧠 Learning Agent: Recording SUCCESS")
            self.context.record(command, "success")
        else:
            print("🧠 Learning Agent: Recording FAILURE")
            self.context.record(command, "failure")

        # Show learning summary
        self.context.summarize()
        # -----------------------------
        # FINAL RESULT
        # -----------------------------
        print("🏁 SYSTEM STATUS: ✅ ALL AGENTS WORKING\n")
    def check_task_success(self):
        """
        Simulated success check
        Replace with vision verification later
        """
        return True  # change logic for real system
