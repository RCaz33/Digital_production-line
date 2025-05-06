from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import Client_Base, Client_Add
from app.database.db_connect import get_db
from app.database import db_Client
from typing import List

# XY_router.py


router = APIRouter(
    prefix="/Client",
    tags=["Client"],
)


# Create batch
@router.post('/', response_model=Client_Base)
def create_Client(request: Client_Add,
                    db: Session = Depends(get_db)):
  return db_Client.create_Client(db, request)

# Read all batch
@router.get('/', response_model=List[Client_Base])
def get_all_Client(db: Session = Depends(get_db)):
  return db_Client.get_all_Client(db)

# Read one batch BY ID
@router.get('/id/{id}', response_model=Client_Base)
def get_Client_id(id: int,
             db: Session = Depends(get_db)):
  return db_Client.get_Client(db, id)

# Read one batch BY NAME
@router.get('/name/{name}', response_model=Client_Base)
def get_Client_name(name: str,
             db: Session = Depends(get_db)):
  print(name)
  return db_Client.get_Client_by_produit_name(db, name)


# Update user
@router.post('/update/{id}')
def update_Client(id: int,
                request: Client_Base,
                db: Session = Depends(get_db)):
  return db_Client.update_Client(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_Client(id: int,
           db: Session = Depends(get_db)):
  return db_Client.delete_Client(db, id)