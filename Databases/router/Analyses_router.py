from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import Analyses_Base
from database.db_connect import get_db
from database import db_Analyses
from typing import List

# MP_router.py


router = APIRouter(
    prefix="/analyses",
    tags=["Analyses"],
)


# Create batch
@router.post('/', response_model=Analyses_Base)
def create_analyse(request: Analyses_Base,
                    db: Session = Depends(get_db)):
  return db_Analyses.create_analyse(db, request)

# Read all batch
@router.get('/', response_model=List[Analyses_Base])
def get_all_analyses(db: Session = Depends(get_db)):
  return db_Analyses.get_all_analyses(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Analyses_Base)
def get_analyses_id(id: int,
             db: Session = Depends(get_db)):
  return db_Analyses.get_analyses(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Analyses_Base)
def get_analyses_code(name: str,
             db: Session = Depends(get_db)):
  return db_Analyses.get_analyses_by_code(db, name)


# Update user
@router.post('/update/{id}')
def update_analyses(id: int,
                request: Analyses_Base,
                db: Session = Depends(get_db)):
  return db_Analyses.update_analyses(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_analyses(id: int,
           db: Session = Depends(get_db)):
  return db_Analyses.delete_analyses(db, id)