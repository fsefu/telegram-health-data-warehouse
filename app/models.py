from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ObjectDetection(Base):
    __tablename__ = "object_detections"

    id = Column(
        Integer, primary_key=True, autoincrement=True
    )  # Auto-incrementing ID for each record
    image_name = Column(String(255), nullable=False)  # Name of the image file
    class_name = Column(String(100), nullable=False)  # Detected object's class
    confidence = Column(Numeric(5, 4), nullable=False)  # Confidence score
    x_min = Column(Numeric(10, 2), nullable=False)  # Bounding box: minimum x-coordinate
    y_min = Column(Numeric(10, 2), nullable=False)  # Bounding box: minimum y-coordinate
    x_max = Column(Numeric(10, 2), nullable=False)  # Bounding box: maximum x-coordinate
    y_max = Column(Numeric(10, 2), nullable=False)  # Bounding box: maximum y-coordinate
    detection_time = Column(DateTime, nullable=False)  # Timestamp of the detection
