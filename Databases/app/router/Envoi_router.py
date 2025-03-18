from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import Envoi_Base, Envoi_Add
from app.database.db_connect import get_db
from app.database import db_Envoi
from typing import List

# OGD_router.py


router = APIRouter(
    prefix="/Envoi",
    tags=["Envoi"],
)


# Create batch
@router.post('/', response_model=Envoi_Base)
def create_Envoi(request: Envoi_Add,
                    db: Session = Depends(get_db)):
  return db_Envoi.create_Envoi(db, request)

# Read all batch
@router.get('/', response_model=List[Envoi_Base])
def get_all_Envoi(db: Session = Depends(get_db)):
  return db_Envoi.get_all_Envoi(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Envoi_Base)
def get_Envoi_id(id: int,
             db: Session = Depends(get_db)):
  return db_Envoi.get_Envoi(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Envoi_Base)
def get_Envoi_name(name: str,
             db: Session = Depends(get_db)):
  print(name)
  return db_Envoi.get_Envoi_by_produit_name(db, name)


# Update user
@router.post('/update/{id}')
def update_Envoi(id: int,
                request: Envoi_Base,
                db: Session = Depends(get_db)):
  return db_Envoi.update_Envoi(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_Envoi(id: int,
           db: Session = Depends(get_db)):
  return db_Envoi.delete_Envoi(db, id)