def normalize(text):
    return text.lower().replace(" ", "").strip()


class NavigationAgent:

    def __init__(self, vision, ultrasonic=None, servo=None, mode="simulation"):
        self.vision = vision
        self.ultrasonic = ultrasonic
        self.servo = servo
        self.mode = mode

    # ---------------------------------
    # SEARCH OBJECT
    # ---------------------------------
    def search_object(self, target):

        print(" Searching for object...")

        # 🔥 Sweep camera (hardware)
        if self.mode == "hardware" and self.servo:
            for angle in range(60, 120, 10):
                self.servo.move(1, angle)

        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":
            print(" No objects found")
            return None

        detections = vision_out["detections"]

        for obj in detections:
            if target is None:
                return obj

            if normalize(target) in normalize(obj["label"]):
                print(f" Found: {obj['label']}")
                return obj

        print(" Target not found during search")
        return None

    # ---------------------------------
    # APPROACH OBJECT (SMART)
    # ---------------------------------
    def approach_object(self, target_obj):

        print(" Approaching object...")

        vision_out = self.vision.get_detections()

        if vision_out["status"] == "no_object":
            print(" Object lost during approach")
            return {"status": "lost"}

        detections = vision_out["detections"]

        # 🔥 Find updated target
        target = None
        for obj in detections:
            if normalize(obj["label"]) == normalize(target_obj["label"]):
                target = obj
                break

        if not target:
            print(" Target disappeared")
            return {"status": "lost"}

        target_x = target["center"][0]

        # ---------------------------------
        # 🔥 OBSTACLE DETECTION (VISION)
        # ---------------------------------
        for obj in detections:

            if obj["label"] == target["label"]:
                continue

            obs_x = obj["center"][0]

            # obstacle in same path
            if abs(obs_x - target_x) < 60:
                print(f" Obstacle blocking: {obj['label']}")

                direction = "left" if obs_x > target_x else "right"

                print(f" Avoiding → move {direction}")

                return {"status": "avoid", "direction": direction}

        # ---------------------------------
        # 🔥 ULTRASONIC (REAL HARDWARE)
        # ---------------------------------
        if self.mode == "hardware" and self.ultrasonic:

            distance = self.ultrasonic.get_distance()

            if distance < 15:
                print(" Obstacle too close")
                return {"status": "blocked"}

            while distance > 15:
                print(f" Distance: {distance} cm → forward")

                if self.servo:
                    self.servo.move(1, 90)

                distance = self.ultrasonic.get_distance()

            print(" Reached object")
            return {"status": "reached"}

        # ---------------------------------
        # 🔥 SIMULATION
        # ---------------------------------
        print(" Path clear → simulated approach")
        return {"status": "reached"}

    # ---------------------------------
    # ALIGN OBJECT
    # ---------------------------------
    def align(self, obj):

        print(" Aligning with object...")

        center_x, center_y = obj["center"]

        if self.mode == "hardware" and self.servo:

            # Smooth alignment
            if center_x < 300:
                self.servo.move(1, 85)
            elif center_x > 340:
                self.servo.move(1, 95)

            if center_y < 220:
                self.servo.move(2, 60)
            elif center_y > 260:
                self.servo.move(2, 75)

        else:
            print(" Simulated alignment")

    # ---------------------------------
    # RETURN HOME
    # ---------------------------------
    def go_home(self):

        print(" Returning to home position")

        if self.mode == "hardware" and self.servo:
            self.servo.move(1, 90)
            self.servo.move(2, 40)
            self.servo.move(3, 40)
        else:
            print(" Simulated home position")