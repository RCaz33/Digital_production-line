from typing import List
from schemas import Batch_OGDStep3_Base, Batch_OGDStep3_Display
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connect import get_db
from database import db_ogd_step3, db_ogd_step0, db_techniciens
# from auth.oauth2 import get_current_user

router = APIRouter(
  prefix='/step3',
  tags=['routes_step3']
)

# Create batch
@router.post('/', response_model=Batch_OGDStep3_Display)
def create_batch_s3(request: Batch_OGDStep3_Base,
                    db: Session = Depends(get_db)):
  return db_ogd_step3.create_batch_s3(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_OGDStep3_Display])
def get_all_batch_s3(db: Session = Depends(get_db)):
  return db_ogd_step3.get_all_batch_s3(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_OGDStep3_Display)
def get_batch_s3_id(id: int,
             db: Session = Depends(get_db)):
  return db_ogd_step3.get_batch_s3(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_OGDStep3_Display)
def get_batch_s3_name(name: str,
             db: Session = Depends(get_db)):
  return db_ogd_step3.get_batch_s3_by_batchname(db, name)


# Update user
@router.post('/{id}/update')
def update_batch_s3(id: int,
                request: Batch_OGDStep3_Base,
                db: Session = Depends(get_db)):
  return db_ogd_step3.update_batch_s3(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_s3(id: int,
           db: Session = Depends(get_db)):
  return db_ogd_step3.delete_user_s3(db, id)