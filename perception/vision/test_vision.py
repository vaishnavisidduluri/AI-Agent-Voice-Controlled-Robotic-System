import cv2
from camera_stream import CameraStream
from object_detector import ObjectDetector
from vision_utils import format_output, draw_detections

camera = CameraStream()
detector = ObjectDetector()

while True:
    frame = camera.get_frame()
    if frame is None:
        break

    detections = detector.detect(frame)

    # Print JSON output
    print(format_output(detections))

    # Draw bounding boxes
    frame = draw_detections(frame, detections)

    cv2.imshow("Vision Simulation", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()