from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas import Matieres_premieres_Base, Matieres_premieres_Add
from database.db_connect import get_db
from database import db_matieres_premieres
from typing import List

# MP_router.py


router = APIRouter(
    prefix="/matieres_premieres",
    tags=["matieres_premieress"],
)


# Create batch
@router.post('/', response_model=Matieres_premieres_Base)
def create_matieres_premieres(request: Matieres_premieres_Add,
                    db: Session = Depends(get_db)):
  return db_matieres_premieres.create_matieres_premieres(db, request)

# Read all batch
@router.get('/', response_model=List[Matieres_premieres_Base])
def get_all_matieres_premieres(db: Session = Depends(get_db)):
  return db_matieres_premieres.get_all_matieres_premieres(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Matieres_premieres_Base)
def get_matieres_premieres_id(id: int,
             db: Session = Depends(get_db)):
  return db_matieres_premieres.get_matieres_premieres(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Matieres_premieres_Base)
def get_matieres_premieres_code(name: str,
             db: Session = Depends(get_db)):
  return db_matieres_premieres.get_matieres_premieres_by_code(db, name)


# Update user
@router.post('/update/{id}')
def update_matieres_premieres(id: int,
                request: Matieres_premieres_Base,
                db: Session = Depends(get_db)):
  return db_matieres_premieres.update_matieres_premieres(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_matieres_premieres(id: int,
           db: Session = Depends(get_db)):
  return db_matieres_premieres.delete_matieres_premieres(db, id)