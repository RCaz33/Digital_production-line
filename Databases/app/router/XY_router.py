from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import Batch_XY_Base, Batch_XY_Add
from app.database.db_connect import get_db
from app.database import db_XY
from typing import List

# XY_router.py


router = APIRouter(
    prefix="/XY",
    tags=["XY"],
)


# Create batch
@router.post('/', response_model=Batch_XY_Base)
def create_batch_XY(request: Batch_XY_Add,
                    db: Session = Depends(get_db)):
  return db_XY.create_batch_XY(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_XY_Base])
def get_all_batch_XY(db: Session = Depends(get_db)):
  return db_XY.get_all_batch_XY(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_XY_Base)
def get_batch_XY_id(id: int,
             db: Session = Depends(get_db)):
  return db_XY.get_batch_XY(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_XY_Base)
def get_batch_XY_name(name: str,
             db: Session = Depends(get_db)):
  print(name)
  return db_XY.get_batch_XY_by_batchname(db, name)


# Update user
@router.post('/update/{id}')
def update_batch_XY(id: int,
                request: Batch_XY_Base,
                db: Session = Depends(get_db)):
  return db_XY.update_batch_XY(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_XY(id: int,
           db: Session = Depends(get_db)):
  return db_XY.delete_batch_XY(db, id)