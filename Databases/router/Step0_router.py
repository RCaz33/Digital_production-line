from typing import List
from fastapi import APIRouter, Depends
from schemas import Batch_OGDstep0_Display, Batch_OGDstep0_Base
from sqlalchemy.orm import Session
from database.db_connect import get_db
from database import db_ogd_step0 
# from auth.oauth2 import get_current_user

router = APIRouter(
  prefix='/step0',
  tags=['step0']
)

# Create batch
@router.post('/', response_model=Batch_OGDstep0_Display)
def create_ogd(request: Batch_OGDstep0_Base,
                db: Session = Depends(get_db)):
  return db_ogd_step0.create_batch_s0(db, request)



# Read all batch
@router.get('/', response_model=List[Batch_OGDstep0_Display])
def get_all_ogds(db: Session = Depends(get_db)):
  return db_ogd_step0.get_all_batch_s0(db)



# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_OGDstep0_Display)
def get_ogd_id(id: int,
             db: Session = Depends(get_db)):
  return db_ogd_step0.get_batch_s0_by_id(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_OGDstep0_Display)
def get_ogd_name(name: str,
             db: Session = Depends(get_db)):
  return db_ogd_step0.get_batch_s0_by_batchname(db, name)


# Update user
@router.post('/{id}/update')
def update_ogd(id: int,
                request: Batch_OGDstep0_Base,
                db: Session = Depends(get_db)):
  return db_ogd_step0.update_batch_s0(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_ogd(id: int,
           db: Session = Depends(get_db)):
  return db_ogd_step0.delete_batch_s0(db, id)