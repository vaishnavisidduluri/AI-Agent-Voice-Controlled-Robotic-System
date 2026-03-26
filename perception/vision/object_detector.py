<<<<<<< HEAD
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame)[0]
        detections = []

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label = self.model.names[class_id]

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            detections.append({
                "id": class_id,
                "label": label,
                "confidence": round(confidence, 2),
                "bbox": [x1, y1, x2, y2],
                "center": [center_x, center_y]
            })

        return detections
=======
def detect_objects():
    """
    YOLO object detection stub for testing.
    Returns list of detections or empty list.
    """
    # Simulate detection for testing
    return [
        {
            "label": "bottle",
            "confidence": 0.85,
            "x": 320,
            "y": 240,
            "bbox": [300, 220, 60, 80]
        }
    ]
>>>>>>> 67f8e8c (Added vision module files)
