from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import Batch_KC8_Base, Batch_KC8_Add
from app.database.db_connect import get_db
from app.database import db_KC8
from typing import List

# KC8_router.py


router = APIRouter(
    prefix="/KC8",
    tags=["KC8"],
)


# Create batch
@router.post('/', response_model=Batch_KC8_Base)
def create_batch_KC8(request: Batch_KC8_Add,
                    db: Session = Depends(get_db)):
  return db_KC8.create_batch_KC8(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_KC8_Base])
def get_all_batch_KC8(db: Session = Depends(get_db)):
  return db_KC8.get_all_batch_KC8(db)

# Read last
@router.get('/last', response_model=Batch_KC8_Base)
def get_last_batch_KC8(db: Session = Depends(get_db)):
  return db_KC8.get_last_batch_KC8(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_KC8_Base)
def get_batch_KC8_id(id: int,
             db: Session = Depends(get_db)):
  return db_KC8.get_batch_KC8(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_KC8_Base)
def get_batch_KC8_name(name: str,
             db: Session = Depends(get_db)):
  return db_KC8.get_batch_KC8_by_batchname(db, name)


# Update user
@router.post('/update/{id}')
def update_batch_KC8(id: int,
                request: Batch_KC8_Base,
                db: Session = Depends(get_db)):
  return db_KC8.update_batch_KC8(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_KC8(id: int,
           db: Session = Depends(get_db)):
  return db_KC8.delete_batch_KC8(db, id)