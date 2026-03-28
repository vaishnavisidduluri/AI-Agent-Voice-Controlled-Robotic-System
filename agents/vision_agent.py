import cv2
from perception.vision.object_detector import detect_objects

class VisionAgent:

    def __init__(self):
        self.detector = detect_objects()
        self.cap = cv2.VideoCapture(0)  # laptop camera

    def get_detections(self):
        try:
            ret, frame = self.cap.read()

            if not ret:
                return {"status": "error", "detections": []}

            detections = self.detector.detect(frame)

            if not detections:
                return {
                    "status": "no_object",
                    "detections": []
                }

            # Show camera (optional but IMPRESSIVE)
            cv2.imshow("Camera Feed", frame)
            cv2.waitKey(1)

            return {
                "status": "ok",
                "detections": detections
            }

        except Exception as e:
            return {
                "status": "error",
                "detections": [],
                "message": str(e)
            }