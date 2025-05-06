from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import Batch_Produit_Base, Batch_Produit_Add
from app.database.db_connect import get_db
from app.database import db_Produit
from typing import List

# XY_router.py


router = APIRouter(
    prefix="/Produit",
    tags=["Produit"],
)


# Create batch
@router.post('/', response_model=Batch_Produit_Base)
def create_batch_Produit(request: Batch_Produit_Add,
                    db: Session = Depends(get_db)):
  return db_Produit.create_batch_Produit(db, request)

# Read all batch
@router.get('/', response_model=List[Batch_Produit_Base])
def get_all_batch_Produit(db: Session = Depends(get_db)):
  return db_Produit.get_all_batch_Produit(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Batch_Produit_Base)
def get_batch_Produit_id(id: int,
             db: Session = Depends(get_db)):
  return db_Produit.get_batch_Produit(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Batch_Produit_Base)
def get_batch_Produit_name(name: str,
             db: Session = Depends(get_db)):
  print(name)
  return db_Produit.get_batch_Produit_by_batchname(db, name)


# Update user
@router.post('/update/{id}')
def update_batch_Produit(id: int,
                request: Batch_Produit_Base,
                db: Session = Depends(get_db)):
  return db_Produit.update_batch_Produit(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_batch_Produit(id: int,
           db: Session = Depends(get_db)):
  return db_Produit.delete_batch_Produit(db, id)