import torch
import cv2
import logging
from pathlib import Path
from torchvision import transforms


# Logger class for handling logging
class Logger:
    def __init__(self, log_file="object_detection.log"):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s:%(levelname)s:%(message)s",
        )

    def log_info(self, message):
        logging.info(message)

    def log_error(self, message):
        logging.error(message)


# YOLO model loader class
class YOLOModel:
    def __init__(self, model_path="yolov5s.pt", device="cpu"):
        self.device = device
        self.logger = Logger()
        try:
            self.model = torch.hub.load("ultralytics/yolov5", "custom", path=model_path)
            self.model.to(self.device)
            self.logger.log_info("YOLO model loaded successfully")
        except Exception as e:
            self.logger.log_error(f"Error loading YOLO model: {e}")

    def predict(self, img):
        try:
            results = self.model(img)
            return results
        except Exception as e:
            self.logger.log_error(f"Error during model inference: {e}")
            return None


# ImageProcessor class for handling image loading and processing
class ImageProcessor:
    def __init__(self, image_dir):
        self.image_dir = Path(image_dir)
        self.transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize((640, 640)),
                transforms.ToTensor(),
            ]
        )
        self.logger = Logger()

    def load_images(self):
        try:
            # image_paths = list(self.image_dir.glob("*.jpg"))
            image_paths = list(self.image_dir.glob("*.jpg")) + list(
                self.image_dir.glob("*.png")
            )

            self.logger.log_info(f"Loaded {len(image_paths)} images for processing")
            return image_paths
        except Exception as e:
            self.logger.log_error(f"Error loading images: {e}")
            return []

    def preprocess_image(self, image_path):
        try:
            img = cv2.imread(str(image_path))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_tensor = self.transform(img).unsqueeze(0)
            return img_tensor
        except Exception as e:
            self.logger.log_error(f"Error preprocessing image {image_path}: {e}")
            return None


# DetectionHandler class for handling detection results
class DetectionHandler:
    def __init__(self):
        self.logger = Logger()

    def process_detections(self, results):
        try:
            # Get the detections directly from the tensor
            detections = (
                results.xyxy[0].cpu().numpy()
            )  # Bounding boxes, confidence, class predictions
            self.logger.log_info("Detection completed successfully")
            return detections
        except Exception as e:
            self.logger.log_error(f"Error processing detections: {e}")
            return None

    def save_detection(self, detections, output_path="detection_results.csv"):
        try:
            detections.to_csv(output_path, index=False)
            self.logger.log_info(f"Detections saved to {output_path}")
        except Exception as e:
            self.logger.log_error(f"Error saving detection results: {e}")


# Main class to orchestrate the entire detection pipeline
class ObjectDetectionPipeline:
    def __init__(self, image_dir, model_path="yolov5s.pt", device="cpu"):
        self.yolo_model = YOLOModel(model_path=model_path, device=device)
        self.image_processor = ImageProcessor(image_dir)
        self.detection_handler = DetectionHandler()
        self.logger = Logger()

    def run(self):
        try:
            # Load and process images
            images = self.image_processor.load_images()
            for image_path in images:
                img_tensor = self.image_processor.preprocess_image(image_path)
                if img_tensor is not None:
                    # Make predictions
                    results = self.yolo_model.predict(img_tensor)
                    if results is not None:
                        # Process and save detections
                        detections = self.detection_handler.process_detections(results)
                        if detections is not None:
                            output_csv = f"results_{image_path.stem}.csv"
                            self.detection_handler.save_detection(
                                detections, output_csv
                            )
        except Exception as e:
            self.logger.log_error(f"Error in detection pipeline: {e}")


# if __name__ == "__main__":
#     # Run the pipeline
#     image_directory = "path_to_images"
#     model_path = "yolov5s.pt"  # Assuming you're using yolov5s model for fast detection
#     detection_pipeline = ObjectDetectionPipeline(
#         image_dir=image_directory, model_path=model_path, device="cpu"
#     )
#     detection_pipeline.run()
