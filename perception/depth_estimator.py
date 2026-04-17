import torch
import cv2
import numpy as np

class DepthEstimator:
    def __init__(self):
        print(" Loading MiDaS Depth Model...")

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
        self.model.to(self.device)
        self.model.eval()

        self.transform = torch.hub.load("intel-isl/MiDaS", "transforms").small_transform

    def estimate(self, frame, bbox):
        """
        frame: camera frame
        bbox: (x1, y1, x2, y2)
        """

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_batch = self.transform(img).to(self.device)

        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        depth_map = prediction.cpu().numpy()

        x1, y1, x2, y2 = bbox

        object_depth = depth_map[y1:y2, x1:x2].mean()

        return float(object_depth)