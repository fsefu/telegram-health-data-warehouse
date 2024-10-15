from pydantic import BaseModel
from datetime import datetime


class ObjectDetectionBase(BaseModel):
    image_name: str
    class_name: str
    confidence: float
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    detection_time: datetime


class ObjectDetectionCreate(ObjectDetectionBase):
    pass


class ObjectDetection(ObjectDetectionBase):
    id: int

    class Config:
        orm_mode = True  # Allow compatibility with ORM models
