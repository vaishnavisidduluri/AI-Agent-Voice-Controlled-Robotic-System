from motion_sequences import MotionPlanner

planner = MotionPlanner()

# simulated vision output
detections = [
    {
        "id": 1,
        "label": "bottle",
        "confidence": 0.91,
        "bbox": [120, 80, 350, 420],
        "center": [235, 250]
    }
]

command = "pick the bottle"

plan = planner.plan(command, detections)

print(plan)