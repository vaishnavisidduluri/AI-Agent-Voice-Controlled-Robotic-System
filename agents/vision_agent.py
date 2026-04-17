import cv2
import time

from perception.vision.object_detector import detect_objects

class VisionAgent:

    def __init__(self):
        self.detector = detect_objects()
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # laptop camera
        self.last_object = None
        self.last_label = None


    def get_detections(self):
        try:
            ret, frame = self.cap.read()


            if not ret:
                self.cap.release()
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                time.sleep(1)
            self.current_frame = frame  # 🔥 ADD THIS

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
    
    def get_object_center(detection):
        x1, y1, x2, y2 = detection["bbox"]
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return cx, cy
    
    def get_frame(self):
        return getattr(self, "current_frame", None)
    

    def track_object(self, detections, target_label):

        if not detections:
            return None

        # 1️⃣ Try exact match first
        candidates = [d for d in detections if target_label in d["label"]]

        if not candidates:
            return None

        # 2️⃣ If no previous object → pick highest confidence
        if self.last_object is None:
            best = max(candidates, key=lambda x: x["confidence"])
            self.last_object = best
            return best

        # 3️⃣ Find closest to previous position
        prev_x, prev_y = self.last_object["center"]

        def distance(obj):
            x, y = obj["center"]
            return ((x - prev_x) ** 2 + (y - prev_y) ** 2) ** 0.5

        best = min(candidates, key=distance)

        self.last_object = best
        return best