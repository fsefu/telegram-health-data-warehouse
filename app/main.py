from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, get_db

# Create the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/detections/", response_model=schemas.ObjectDetection)
def create_detection(
    detection: schemas.ObjectDetectionCreate, db: Session = Depends(get_db)
):
    return crud.create_object_detection(db=db, detection=detection)


@app.get("/detections/{detection_id}", response_model=schemas.ObjectDetection)
def read_detection(detection_id: int, db: Session = Depends(get_db)):
    db_detection = crud.get_object_detection(db, detection_id)
    if db_detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return db_detection


@app.get("/detections/", response_model=list[schemas.ObjectDetection])
def read_detections(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    detections = crud.get_object_detections(db, skip=skip, limit=limit)
    return detections


@app.put("/detections/{detection_id}", response_model=schemas.ObjectDetection)
def update_detection(
    detection_id: int,
    detection: schemas.ObjectDetectionCreate,
    db: Session = Depends(get_db),
):
    updated_detection = crud.update_object_detection(db, detection_id, detection)
    if updated_detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return updated_detection


@app.delete("/detections/{detection_id}", response_model=schemas.ObjectDetection)
def delete_detection(detection_id: int, db: Session = Depends(get_db)):
    deleted_detection = crud.delete_object_detection(db, detection_id)
    if deleted_detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return deleted_detection
