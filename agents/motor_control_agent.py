import yaml

class MotorControlAgent:

    def __init__(self, config_path="config/servo_limits.yaml"):
        with open(config_path, "r") as f:
            self.limits = yaml.safe_load(f)

    def validate(self, steps):

        for step in steps:

            if "servo_id" in step:

                sid = step["servo_id"]
                angle = step["angle"]

                if sid not in [1, 2, 3, 4, 5, 6]:
                    return {"safe": False, "reason": f"Servo {sid} not defined"}

                if not (0 <= angle <= 180):
                    return {"safe": False, "reason": f"Servo {sid} out of range"}

        return {"safe": True}
    

class MobileBase:
    def move_forward(self):
        print("Moving forward")

    def stop(self):
        print("Stopping")

    def turn_left(self):
        print("Turning left")

    def turn_right(self):
        print("Turning right")