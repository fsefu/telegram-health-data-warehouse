import os
import logging
import torch
import cv2
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename="logs/yolo_detection.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


class YOLODetector:
    """Class to handle YOLOv5 object detection."""

    def __init__(self, model_name="yolov5s"):
        """Initializes the YOLO object detector with the specified model."""
        self.model = self.load_model(model_name)

    def load_model(self, model_name):
        """Load the YOLOv5 model from torch hub."""
        logging.info(f"Loading YOLOv5 model: {model_name}")
        return torch.hub.load("ultralytics/yolov5", model_name)

    def detect_objects_in_image(self, image_path):
        """Detect objects in a single image."""
        img = cv2.imread(image_path)
        results = self.model(img)
        detections = []

        for detection in results.xyxy[0]:
            xmin, ymin, xmax, ymax, confidence, class_id = detection[:6]
            class_name = self.model.names[int(class_id)]
            detections.append(
                {
                    "image_name": os.path.basename(image_path),
                    "class_name": class_name,
                    "confidence": confidence.item(),
                    "x_min": xmin.item(),
                    "y_min": ymin.item(),
                    "x_max": xmax.item(),
                    "y_max": ymax.item(),
                    "detection_time": datetime.now(),
                }
            )
            logging.info(
                f"Detected {class_name} with confidence {confidence:.2f} in {os.path.basename(image_path)}"
            )

        return detections

    def process_image_folder(self, image_folder, db_handler):
        """Processes all images in the given folder and performs object detection."""
        all_detections = []
        for image_file in os.listdir(image_folder):
            if image_file.endswith((".jpg", ".png")):
                image_path = os.path.join(image_folder, image_file)
                logging.info(f"Processing image: {image_path}")
                detections = self.detect_objects_in_image(image_path)
                all_detections.extend(detections)

        if all_detections:
            db_handler.store_detections(all_detections)
        else:
            logging.info("No detections to store.")

    def run(self, image_folder, db_handler):
        """Run the object detection on the specified image folder and store results using db_handler."""
        try:
            logging.info("Starting object detection...")
            self.process_image_folder(image_folder, db_handler)
            logging.info("Object detection completed.")
        except Exception as e:
            logging.error(f"An error occurred during object detection: {e}")
