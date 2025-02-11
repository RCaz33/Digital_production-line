from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import Analyses_UV_Base, Analyses_UV_Add
from database.db_connect import get_db
from database import db_Analyses_UV
from typing import List

# MP_router.py


router = APIRouter(
    prefix="/analyses_UV",
    tags=["Analyses_UV"],
)


# Create batch
@router.post('/', response_model=Analyses_UV_Base)
def create_analyse_UV(request: Analyses_UV_Add,
                    db: Session = Depends(get_db)):
  return db_Analyses_UV.create_analyse_UV(db, request)

# Read all batch
@router.get('/', response_model=List[Analyses_UV_Base])
def get_all_analyses_UV(db: Session = Depends(get_db)):
  return db_Analyses_UV.get_all_analyses_UV(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Analyses_UV_Base)
def get_analyses_id_UV(id: int,
             db: Session = Depends(get_db)):
  return db_Analyses_UV.get_analyse_id_UV(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Analyses_UV_Base)
def get_analyse_UV_by_name(name: str,
             db: Session = Depends(get_db)):
  return db_Analyses_UV.get_analyse_UV_by_name(db, name)


# Update user
@router.post('/update/{id}')
def update_analyses_UV(id: int,
                request: Analyses_UV_Base,
                db: Session = Depends(get_db)):
  return db_Analyses_UV.update_analyses_UV(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_analyses_UV(id: int,
           db: Session = Depends(get_db)):
  return db_Analyses_UV.delete_analyses_UV(db, id)