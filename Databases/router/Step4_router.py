from typing import List
from schemas import Batch_OGDStep4_Base, Batch_OGDStep4_Display
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connect import get_db
from database import db_ogd_step4, db_ogd_step0, db_techniciens
# from auth.oauth2 import get_current_user

router = APIRouter(
  prefix='/step4',
  tags=['routes_step4']
)

# Create batch
@router.post('/', response_model=Batch_OGDStep4_Display)
def create_batch_s4(request: Batch_OGDStep4_Base,
                    db: Session = Depends(get_db)):
  return db_ogd_step4.create_batch_s4(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_OGDStep4_Display])
def get_all_batch_s4(db: Session = Depends(get_db)):
  return db_ogd_step4.get_all_batch_s4(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_OGDStep4_Display)
def get_batch_s4_id(id: int,
             db: Session = Depends(get_db)):
  return db_ogd_step4.get_batch_s4(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_OGDStep4_Display)
def get_batch_s4_name(name: str,
             db: Session = Depends(get_db)):
  return db_ogd_step4.get_batch_s4_by_batchname(db, name)


# Update user
@router.post('/{id}/update')
def update_batch_s4(id: int,
                request: Batch_OGDStep4_Base,
                db: Session = Depends(get_db)):
  return db_ogd_step4.update_batch_s4(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_s4(id: int,
           db: Session = Depends(get_db)):
  return db_ogd_step4.delete_user_s4(db, id)