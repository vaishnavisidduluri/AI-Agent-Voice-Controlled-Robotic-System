import time

from agents.speech_agent import SpeechAgent
from agents.vision_agent import VisionAgent
from agents.learning_agent import LearningAgent
from agents.motor_control_agent import MotorControlAgent
from agents.navigation_agent import NavigationAgent

from planner.task_planner import TaskPlanner
from planner.ik_solver import IKSolver

from perception.depth_estimator import DepthEstimator

from simulation.mock_servo import MockServo as ServoController


class MasterAgent:

    def __init__(self):
        self.speech = SpeechAgent()
        self.vision = VisionAgent()
        self.context = LearningAgent()
        self.safety = MotorControlAgent()
        self.planner = TaskPlanner()
        self.servo = ServoController()
        self.ik = IKSolver()
        self.depth = DepthEstimator()

        self.navigation = NavigationAgent(
            vision=self.vision,
            ultrasonic=None,
            servo=self.servo,
            mode="simulation"  # change to "hardware"
        )

    def run(self):
        print(" AI Robotic Arm System Initialized...\n")

        while True:
            self.process_cycle()
            time.sleep(1)

    def estimate_depth(self, obj):

        frame = self.vision.get_frame()

        if frame is None:
            return 30  # fallback

        bbox = obj.get("bbox")

        if not bbox:
            return 30

        depth = self.depth.estimate(frame, bbox)

        print(f" Estimated Depth: {depth}")

        return depth

    def check_grasp_success(self):
    # 🔥 SIMPLE LOGIC (can improve later)

        if not self.context.holding:
            return False

        # Optional: verify object still visible
        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":
            return True  # object likely picked

        for d in vision_out["detections"]:
            if d["label"] == self.context.memory.get("last_object"):
                return False  # still visible → not picked

        return True

    def verify_grasp(self, obj):

        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":
            print(" Object disappeared → assuming grasp success")
            return True

        labels = [d["label"] for d in vision_out["detections"]]

        if obj["label"] in labels:
            print(" Object still visible → grasp failed")
            return False
        else:
            print(" Object not visible → grasp success")
            return True
    def retry_grasp(self, obj):

        print(" Attempting grasp...")

        self.servo.control_gripper("close")
        time.sleep(1)

        if self.verify_grasp(obj):
            print(" Grasp successful")
            return True

        print(" Grasp failed → retrying...")

        for attempt in range(2):

            print(f" Retry attempt {attempt + 1}...")

            # 🔥 small reposition
            self.servo.move(2, 60 + attempt * 5)
            time.sleep(0.5)

            self.servo.control_gripper("open")
            time.sleep(0.5)

            self.servo.control_gripper("close")
            time.sleep(1)

            if self.verify_grasp(obj):
                print(" Grasp successful on retry!")
                return True

        print(" Failed to grasp object after retries")
        return False    
    
    def process_cycle(self):

        # 1️⃣ SPEECH INPUT
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

        if command.get("object"):
            print(f' Object: {command["object"]}')

        self.context.update_memory("last_command", command)

        # -----------------------------
        # 🔥 DROP SAFETY
        # -----------------------------
        if command["action"] == "drop":

            if not self.context.holding:
                print("❌ Nothing to drop")
                return

            print(" Drop command → executing directly")

            self.servo.control_gripper("open")

            self.context.holding = False
            self.context.state = "idle"

            self.context.update_after_action("drop", success=True)

            print(" Task Completed Successfully")
            return

        # -----------------------------
        # ✅ MOVE (NO VISION NEEDED)
        # -----------------------------
        if command["action"] == "move":
            print(f" Moving {command.get('destination')}")

            plan = self.planner.plan_task(command, [], self.context)

            if plan["status"] != "ok":
                print(plan["message"])
                return

            for step in plan["steps"]:
                if "move" in step:
                    print(f"[SIM] Moving {step['move']}")
                    time.sleep(step.get("delay", 1))

            print("\n Task Completed Successfully")
            return

        # -----------------------------
        # 2️⃣ VISION
        # -----------------------------
        print("\n Vision Agent → Scanning environment...")
        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":
            print(" Lost object → using last known position")

            if self.vision.last_object:
                obj = self.vision.last_object
            else:
                return
        else:
            detections = vision_out["detections"]
            obj = self.vision.track_object(detections, command["object"])

        detections = vision_out["detections"]

        print("\n Detected Objects:")
        for d in detections:
            print(f" - {d['label']} (conf: {d['confidence']})")

        # -----------------------------
        # 🔥 OBJECT MATCHING
        # -----------------------------
        def normalize(text):
            return text.lower().replace(" ", "").strip()

        if command.get("object"):

            target_label = command["object"]

            obj = self.vision.track_object(detections, target_label)

            if obj is None:
                print(f" Object '{command['object']}' not found")
                return

            print(f" Tracked Object: {obj['label']}")

            


        else:
            obj = detections[0]

        print(f"\n Target Object: {obj['label']}")
        print(f" Center: {obj['center']}")

        self.context.update_memory("last_object", obj["label"])

        # -----------------------------
        # 3️⃣ INITIAL OFFSET (ROUGH)
        # -----------------------------
        cx, cy = obj["center"]

        # 🔥 Extract bounding box
        x1, y1, x2, y2 = obj["bbox"]

        # 🔥 Smart grasp point (slightly above center)
        grasp_x = int((x1 + x2) / 2)
        grasp_y = int(y1 + (y2 - y1) * 0.3)  # 30% from top

        print(f" Smart Grasp Point: ({grasp_x}, {grasp_y})")

        offset_x = cx - 320
        offset_y = cy - 240

        adjust_y = int(offset_y * 0.05)

        print(f" X Offset: {offset_x}")
        print(f" Y Offset: {offset_y}")

        # -----------------------------
        # 4️⃣ NAVIGATION
        # -----------------------------
        print("\n Navigation → Starting...")

        print(" Navigation → Approaching...")
        result = self.navigation.approach_object(obj)

        if result is False:
            print(" Movement blocked")
            return

        if isinstance(result, dict) and result.get("status") == "avoid":
            direction = result["direction"]
            print(f" Avoiding obstacle → {direction}")
            self.servo.move(1, 60 if direction == "left" else 120)
            time.sleep(1)

        # -----------------------------
        # 🔥 ALIGN WITH FEEDBACK
        # -----------------------------
        print(" Navigation → Aligning with feedback...")

        final_adjust_x = 0

        for _ in range(5):

            vision_out = self.vision.get_detections()

            if vision_out["status"] == "no_object":
                print(" Lost object")
                return

            # 🔥 KEEP TARGET LOCKED
            for d in vision_out["detections"]:
                if obj["label"] in d["label"]:
                    obj = d
                    break

            center_x, center_y = obj["center"]

            offset_x = center_x - 320
            offset_y = center_y - 240

            if abs(offset_x) < 20 and abs(offset_y) < 20:
                print(" Object aligned")
                break

            current_angle = 90

            adjust_x = int(offset_x * 0.05)
            current_angle += adjust_x

            self.servo.move(1, current_angle)
            time.sleep(0.3)

        # -----------------------------
        # 🔥 UPDATE TARGET AFTER ALIGN
        # -----------------------------
        cx, cy = obj["center"]

        # 🔥 Convert 2D → 3D (scaled + clamped)
        x = (grasp_x - 320) * 0.1
        y = (grasp_y - 240) * 0.1
        raw_depth = self.estimate_depth(obj)
        z = raw_depth - 2

        # 🔥 Clamp to robot workspace
        x = max(-15, min(15, x))
        y = max(5, min(20, y))
        z = max(5, min(25, z))

        target_position = (x, y, z)

        print(f" Target 3D Position: {target_position}")
        
        # -----------------------------
        # 5️⃣ IK SOLVER
        # -----------------------------
        print("\n IK → Computing joint angles...")

        angles = self.ik.solve(*target_position)

        if not angles:
            print(" IK failed → trying fallback position")

            angles = {
                "servo1": 90,
                "servo2": 60,
                "servo3": 50
            }

        steps = [
            {"gripper": "open", "delay": 0.5},
            {"servo_id": 1, "angle": angles["servo1"], "delay": 0.5},
            {"servo_id": 2, "angle": angles["servo2"], "delay": 0.5},
            {"servo_id": 3, "angle": angles["servo3"], "delay": 0.5},

            # 🔥 NEW: descend slightly
            {"servo_id": 3, "angle": angles["servo3"] + 10, "delay": 0.5},

            {"gripper": "close", "delay": 0.5},
            {"servo_id": 3, "angle": max(0, min(180, angles["servo3"] - 20)), "delay": 0.5}
        ]

        print(" Generated IK Steps:", steps)

        # -----------------------------
        # 🔥 APPLY ALIGNMENT
        # -----------------------------
        for step in steps:
            if step.get("servo_id") == 1:
                step["angle"] = max(0, min(180, step["angle"] + adjust_x))

            if step.get("servo_id") in [2, 3]:
                step["angle"] = max(0, min(180, step["angle"] - adjust_y))

        # -----------------------------
        # 🔒 SAFETY
        # -----------------------------
        print("\n Safety Agent → Validating plan...")
        safety = self.safety.validate(steps)

        if not safety["safe"]:
            print(f" Unsafe: {safety['reason']}")
            return

        print(" Plan Approved")

        # -----------------------------
        # 6️⃣ EXECUTION
        # -----------------------------
        print("\n Execution Agent → Executing...")

        for i, step in enumerate(steps, 1):

            print(f"\n Step {i}:")

            if "servo_id" in step:
                self.servo.move(step["servo_id"], step["angle"])

            elif "gripper" in step:
                self.servo.control_gripper(step["gripper"])

                if step["gripper"] == "close":
                    print(" Attempting grasp...")

                    success = self.retry_grasp(obj)

                    if success:
                        self.context.holding = True
                        self.context.state = "holding"
                    else:
                        print(" Grasp ultimately failed")
                        return

                elif step["gripper"] == "open":
                    self.context.holding = False
                    self.context.state = "idle"

            elif "move" in step:
                print(f"[SIM] Moving {step['move']}")

            time.sleep(step.get("delay", 0.5))

        # -----------------------------
        # 🔥 BRING FINAL STEP
        # -----------------------------
        if command["action"] == "bring":
            print("\n Returning Home...")
            self.navigation.go_home()

            print(" Dropping object...")
            self.servo.control_gripper("open")

            self.context.holding = False
            self.context.state = "idle"

        self.context.update_after_action(command["action"], success=True)
        self.vision.last_object = None
        print(f"\n STATE → {self.context.state}, HOLDING → {self.context.holding}")
        print("\n Task Completed Successfully")