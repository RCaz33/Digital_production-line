from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import Batch_XX_Base, Batch_XX_Add
from app.database.db_connect import get_db
from app.database import db_XX
from typing import List

# XX_router.py


router = APIRouter(
    prefix="/XX",
    tags=["XX"],
)


# Create batch
@router.post('/', response_model=Batch_XX_Base)
def create_batch_XX(request: Batch_XX_Add,
                    db: Session = Depends(get_db)):
  return db_XX.create_batch_XX(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_XX_Base])
def get_all_batch_XX(db: Session = Depends(get_db)):
  return db_XX.get_all_batch_XX(db)

# Read last
@router.get('/last', response_model=Batch_XX_Base)
def get_last_batch_XX(db: Session = Depends(get_db)):
  return db_XX.get_last_batch_XX(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_XX_Base)
def get_batch_XX_id(id: int,
             db: Session = Depends(get_db)):
  return db_XX.get_batch_XX(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_XX_Base)
def get_batch_XX_name(name: str,
             db: Session = Depends(get_db)):
  return db_XX.get_batch_XX_by_batchname(db, name)


# Update user
@router.post('/update/{id}')
def update_batch_XX(id: int,
                request: Batch_XX_Base,
                db: Session = Depends(get_db)):
  return db_XX.update_batch_XX(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_XX(id: int,
           db: Session = Depends(get_db)):
  return db_XX.delete_batch_XX(db, id)