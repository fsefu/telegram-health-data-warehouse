from sqlalchemy.orm import Session
from .models import ObjectDetection
from .schemas import ObjectDetectionCreate


def create_object_detection(db: Session, detection: ObjectDetectionCreate):
    db_detection = ObjectDetection(**detection.dict())
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection


def get_object_detection(db: Session, detection_id: int):
    return db.query(ObjectDetection).filter(ObjectDetection.id == detection_id).first()


def get_object_detections(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ObjectDetection).offset(skip).limit(limit).all()


def update_object_detection(
    db: Session, detection_id: int, detection: ObjectDetectionCreate
):
    db_detection = get_object_detection(db, detection_id)
    if db_detection:
        for key, value in detection.dict().items():
            setattr(db_detection, key, value)
        db.commit()
        db.refresh(db_detection)
        return db_detection
    return None


def delete_object_detection(db: Session, detection_id: int):
    db_detection = get_object_detection(db, detection_id)
    if db_detection:
        db.delete(db_detection)
        db.commit()
        return db_detection
    return None
