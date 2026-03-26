from perception.vision.object_detector import detect_objects

class VisionAgent:

    def get_detections(self):
        try:
            detections = detect_objects()

            if not detections:
                return {
                    "status": "no_object",
                    "detections": []
                }

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