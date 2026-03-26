class TaskPlanner:

    def __init__(self):
        self.state = "IDLE"

    def plan_task(self, command, detections):
        self.state = "IDLE"

        if not command:
            return {"status": "error", "message": "No command"}

        action = command.get("action")

        if action == "pick":
            return self._fsm_pick(detections)

        if action == "move":
            return self._plan_move(command["destination"])

        if action == "open_gripper":
            return {"status": "ok", "steps":[{"gripper":"open", 'delay': 0.5}]}

        if action == "close_gripper":
            return {"status": "ok", "steps":[{"gripper":"close", 'delay': 0.5}]}

        if action == "stop":
            return {"status":"ok","steps":[]}

        return {"status":"error","message":"Unknown action"}

    # ---------------------------------
    # FSM for PICK task
    # ---------------------------------

    def _fsm_pick(self, detections):

        steps = []

        while True:

            # STATE 1
            if self.state == "IDLE":
                self.state = "LOCATE_OBJECT"

            # STATE 2
            elif self.state == "LOCATE_OBJECT":

                if not detections:
                    return {"status":"error","message":"Object not detected"}

                obj = detections[0]
                self.target = obj
                self.state = "MOVE_TO_OBJECT"

            # STATE 3
            elif self.state == "MOVE_TO_OBJECT":

                steps.append({"servo_id":1,"angle":90, 'delay': 0.5})
                steps.append({"servo_id":2,"angle":50, 'delay': 0.5})

                self.state = "LOWER_ARM"

            # STATE 4
            elif self.state == "LOWER_ARM":

                steps.append({"servo_id":3,"angle":70, 'delay': 0.5})

                self.state = "CLOSE_GRIPPER"

            # STATE 5
            elif self.state == "CLOSE_GRIPPER":

                steps.append({"gripper":"close", 'delay': 0.5})

                self.state = "LIFT_OBJECT"

            # STATE 6
            elif self.state == "LIFT_OBJECT":

                steps.append({"servo_id":3,"angle":40, 'delay': 0.5})

                self.state = "DONE"

            # FINAL
            elif self.state == "DONE":

                self.state = "IDLE"

                return {
                    "status":"ok",
                    "steps":steps
                }

    # ---------------------------------

    def _plan_move(self, direction):

        if direction == "left":
            return {"status":"ok","steps":[{"servo_id":1,"angle":60, 'delay': 0.5}]}

        if direction == "right":
            return {"status":"ok","steps":[{"servo_id":1,"angle":120, 'delay': 0.5}]}

        if direction == "up":
            return {"status":"ok","steps":[{"servo_id":2,"angle":40, 'delay': 0.5}]}

        if direction == "down":
            return {"status":"ok","steps":[{"servo_id":2,"angle":80, 'delay': 0.5}]}

        return {"status":"error","message":"Invalid direction"}



if __name__ == "__main__":

    planner = TaskPlanner()

    # example parsed command
    parsed_command = {
        "action": "pick"
    }

    # example detections from object detector
    detections = [
        {"label": "bottle", "x": 100, "y": 200}
    ]

    result = planner.plan_task(parsed_command, detections)

    print("Planner Output:")
    print(result)

