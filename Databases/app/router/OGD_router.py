from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import Batch_OGD_Base, Batch_OGD_Add
from app.database.db_connect import get_db
from app.database import db_OGD
from typing import List

# OGD_router.py


router = APIRouter(
    prefix="/OGD",
    tags=["OGD"],
)


# Create batch
@router.post('/', response_model=Batch_OGD_Base)
def create_batch_OGD(request: Batch_OGD_Add,
                    db: Session = Depends(get_db)):
  return db_OGD.create_batch_OGD(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_OGD_Base])
def get_all_batch_OGD(db: Session = Depends(get_db)):
  return db_OGD.get_all_batch_OGD(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_OGD_Base)
def get_batch_OGD_id(id: int,
             db: Session = Depends(get_db)):
  return db_OGD.get_batch_OGD(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_OGD_Base)
def get_batch_OGD_name(name: str,
             db: Session = Depends(get_db)):
  print(name)
  return db_OGD.get_batch_OGD_by_batchname(db, name)


# Update user
@router.post('/update/{id}')
def update_batch_OGD(id: int,
                request: Batch_OGD_Base,
                db: Session = Depends(get_db)):
  return db_OGD.update_batch_OGD(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_OGD(id: int,
           db: Session = Depends(get_db)):
  return db_OGD.delete_batch_OGD(db, id)