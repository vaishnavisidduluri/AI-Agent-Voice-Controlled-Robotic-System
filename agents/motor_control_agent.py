import yaml

class MotorControlAgent:

    def __init__(self, config_path="config/servo_limits.yaml"):
        with open(config_path, "r") as f:
            self.limits = yaml.safe_load(f)

    def validate(self, steps):
        for step in steps:
            if "servo_id" in step:
                sid = str(step["servo_id"])
                angle = step["angle"]

                if sid not in self.limits:
                    return {"safe": False, "reason": f"Servo {sid} not defined"}

                min_angle = self.limits[sid]["min"]
                max_angle = self.limits[sid]["max"]

                if not (min_angle <= angle <= max_angle):
                    return {
                        "safe": False,
                        "reason": f"Servo {sid} out of range"
                    }

        return {"safe": True, "reason": None}
    

class MobileBase:
    def move_forward(self):
        print("Moving forward")

    def stop(self):
        print("Stopping")

    def turn_left(self):
        print("Turning left")

    def turn_right(self):
        print("Turning right")