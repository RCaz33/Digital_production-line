from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import Prediction_Base, Prediction_Add
from app.database.db_connect import get_db
from app.database import db_Predictions
from typing import List

# OGD_router.py


router = APIRouter(
    prefix="/Predictions",
    tags=["Predictions"],
)


# Create batch
@router.post('/', response_model=Prediction_Base)
def create_Prediction(request: Prediction_Add,
                    db: Session = Depends(get_db)):
  return db_Predictions.create_prediction(db, request)

# Read all batch
@router.get('/', response_model=List[Prediction_Base])
def get_all_Prediction(db: Session = Depends(get_db)):
  return db_Predictions.get_all_Prediction(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Prediction_Base)
def get_Prediction_id(id: int,
             db: Session = Depends(get_db)):
  return db_Predictions.get_Prediction(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Prediction_Base)
def get_Prediction_type(name: str,
             db: Session = Depends(get_db)):
  print(name)
  return db_Predictions.get_Prediction_by_type(db, name)


# Update user
@router.post('/update/{id}')
def update_Prediction(id: int,
                request: Prediction_Base,
                db: Session = Depends(get_db)):
  return db_Predictions.update_Prediction(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_Prediction(id: int,
           db: Session = Depends(get_db)):
  return db_Predictions.delete_Prediction(db, id)