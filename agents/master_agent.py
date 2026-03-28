import time

from agents.speech_agent import SpeechAgent
from agents.vision_agent import VisionAgent
from agents.learning_agent import LearningAgent
from agents.motor_control_agent import MotorControlAgent

from planner.task_planner import TaskPlanner

from simulation.mock_servo import MockServo as ServoController


class MasterAgent:

    def __init__(self):
        self.speech = SpeechAgent()
        self.vision = VisionAgent()
        self.context = LearningAgent()
        self.safety = MotorControlAgent()
        self.planner = TaskPlanner()
        self.servo = ServoController()

    def run(self):
        print(" AI Robotic Arm System Initialized...\n")

        while True:
            self.process_cycle()
            time.sleep(1)

    def process_cycle(self):

        # 1️ SPEECH INPUT
        print("\n Speech Agent → Listening...")

        speech_out = self.speech.get_command()

        if speech_out["status"] == "no_input":
            return

        if speech_out["status"] != "ok":
            print("❌ Speech Agent → Error")
            return

        command = speech_out["command"]

        print(" Wake Word Detected: robot")
        print(f' Command: {command["action"]}')
        print(f' Confidence: {command["confidence"]}')

        if command.get("destination"):
            print(f' Direction: {command["destination"]}')

        if command.get("object"):
            print(f' Object: {command["object"]}')

        self.context.update("last_command", command)

        # 2️ VISION
        print("\n Vision Agent → Scanning environment...")

        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":
            print(" Vision Agent → No object detected")
            return

        detections = vision_out["detections"]
        obj = detections[0]

        print(f' Detected Object: {obj["label"]}')
        print(f' Confidence: {obj["confidence"]}')
        print(f' Center Position: {obj["center"]}')

        self.context.update("last_object", obj["label"])

        # 3️ PLANNING
        print("\n Planner Agent → Generating plan...")

        plan = self.planner.plan_task(command, detections)

        if plan["status"] != "ok":
            print("❌ Planner Agent → Failed")

            #  Retry logic using Learning Agent
            if self.context.should_retry():
                self.context.increase_retry()

                suggestion = self.context.suggest_action()

                if suggestion:
                    print(" Using learned action instead...")
                    command = suggestion

                    plan = self.planner.plan_task(command, detections)

                    if plan["status"] != "ok":
                        return
                else:
                    return
            else:
                print("⚠️ Max retries reached. Skipping task")
                self.context.reset_retry()
                return

        steps = plan["steps"]

        print(f' Action: {command["action"]}')

        if command.get("destination"):
            print(f' Direction: {command["destination"]}')

        if command.get("object"):
            print(f' Target Object: {command["object"]}')

        print(" Generated Steps:")
        print(f" Total Steps: {len(steps)}")

        for i, step in enumerate(steps, 1):
            print(f"\n   Step {i}:")

            if "servo_id" in step:
                print(f"      → Servo ID   : {step['servo_id']}")
                print(f"      → Angle      : {step['angle']}°")

            if "gripper" in step:
                print(f"      → Gripper    : {step['gripper']}")

            if "delay" in step:
                print(f"      → Delay      : {step['delay']} sec")
        # 4️ SAFETY CHECK
        print("\n Safety Agent → Validating plan...")

        safety = self.safety.validate(steps)

        if not safety["safe"]:
            print(f' Unsafe Plan: {safety["reason"]}')
            return

        print(" Plan Approved")

        # 5️ EXECUTION
        print("\n Execution Agent → Executing...")

        for i, step in enumerate(steps, 1):
            print(f"\n Executing Step {i}:")

            if "servo_id" in step:
                print(f"   → Moving Servo {step['servo_id']} to {step['angle']}°")
                print(f"   → Delay: {step.get('delay', 0.5)} sec")
                self.servo.move(step["servo_id"], step["angle"])

            elif "gripper" in step:
                print(f"   → Gripper Action: {step['gripper']}")
                print(f"   → Delay: {step.get('delay', 0.5)} sec")
                self.servo.control_gripper(step["gripper"])

            time.sleep(step.get("delay", 0.5))
        # 6️ FEEDBACK
        success = self.check_task_success()

        if success:
            print("\n Task Completed Successfully")
            self.context.record(command, "success")
            self.context.update("last_result", "success")
            self.context.reset_retry()
            print(" Learning Agent → Stored experience\n")

        else:
            print("\n❌ Task Failed → Retrying...\n")

            retry = self.context.get("retry_count") + 1
            self.context.update("retry_count", retry)

            if retry >= 3:
                print("⚠️ Max retries reached. Aborting.\n")
                self.context.reset_retry()

    def check_task_success(self):
        return True