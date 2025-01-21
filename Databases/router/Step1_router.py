from typing import List
from schemas import Batch_OGDstep1_Base, Batch_OGDStep1_Display
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connect import get_db
from database import db_ogd_step1, db_ogd_step0, db_techniciens
# from auth.oauth2 import get_current_user

router = APIRouter(
  prefix='/step1',
  tags=['routes_step1']
)

# Create batch
@router.post('/', response_model=Batch_OGDStep1_Display)
def create_batch_s1(request: Batch_OGDstep1_Base,
                    db: Session = Depends(get_db)):
  return db_ogd_step1.create_batch_s1(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_OGDStep1_Display])
def get_all_batch_s1(db: Session = Depends(get_db)):
  return db_ogd_step1.get_all_batch_s1(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_OGDStep1_Display)
def get_batch_s1_id(id: int,
             db: Session = Depends(get_db)):
  return db_ogd_step1.get_batch_s1(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_OGDStep1_Display)
def get_batch_s1_name(name: str,
             db: Session = Depends(get_db)):
  return db_ogd_step1.get_batch_s1_by_batchname(db, name)


# Update user
@router.post('/{id}/update')
def update_batch_s1(id: int,
                request: Batch_OGDstep1_Base,
                db: Session = Depends(get_db)):
  return db_ogd_step1.update_batch_s1(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_s1(id: int,
           db: Session = Depends(get_db)):
  return db_ogd_step1.delete_user_s1(db, id)