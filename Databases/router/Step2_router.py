from typing import List
from schemas import Batch_OGDstep2_Base, Batch_OGDStep2_Display
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connect import get_db
from database import db_ogd_step2, db_ogd_step0, db_techniciens
# from auth.oauth2 import get_current_user

router = APIRouter(
  prefix='/step2',
  tags=['routes_step2']
)

# Create batch
@router.post('/', response_model=Batch_OGDStep2_Display)
def create_batch_s2(request: Batch_OGDstep2_Base,
                    db: Session = Depends(get_db)):
  return db_ogd_step2.create_batch_s2(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_OGDStep2_Display])
def get_all_batch_s2(db: Session = Depends(get_db)):
  return db_ogd_step2.get_all_batch_s2(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_OGDStep2_Display)
def get_batch_s2_id(id: int,
             db: Session = Depends(get_db)):
  return db_ogd_step2.get_batch_s2(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_OGDStep2_Display)
def get_batch_s2_name(name: str,
             db: Session = Depends(get_db)):
  return db_ogd_step2.get_batch_s2_by_batchname(db, name)


# Update user
@router.post('/{id}/update')
def update_batch_s2(id: int,
                request: Batch_OGDstep2_Base,
                db: Session = Depends(get_db)):
  return db_ogd_step2.update_batch_s2(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_s2(id: int,
           db: Session = Depends(get_db)):
  return db_ogd_step2.delete_user_s2(db, id)