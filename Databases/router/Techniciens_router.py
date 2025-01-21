from typing import List
from schemas import Technicien_Base, Technicien_Display, Technicien_Create_record
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db_connect import get_db
from database import db_techniciens
# from auth.oauth2 import get_current_user

router = APIRouter(
  prefix='/techniciens',
  tags=['routes_techniciens']
)

# Create Tech
@router.post('/', response_model=Technicien_Display)
def create_tech(request: Technicien_Create_record,
                    db: Session = Depends(get_db)):
  return db_techniciens.create_technicien(db, request)

# Read all Techs
@router.get('/', response_model=List[Technicien_Display])
def get_all_techs(db: Session = Depends(get_db)):
  return db_techniciens.get_all_tech(db)

# Read one Tech by id
@router.get('/id/{id}', response_model=Technicien_Display)
def get_one_tech_id(id: int,
             db: Session = Depends(get_db)):
  return db_techniciens.get_tech_by_id(db, id)

# Read one Tech by Initiales
@router.get('/initials/{name}', response_model=Technicien_Display)
def get_one_tech_name(initiales: str,
             db: Session = Depends(get_db)):
  return db_techniciens.get_tech_by_initials(db, initiales)


# Update Tech
@router.post('/update/{id}')
def update_tech(id: int,
                request: Technicien_Base,
                db: Session = Depends(get_db)):
  return db_techniciens.update_tech(db, id, request)

# Delete user
@router.get('/delete/{id}')
def delete_tech(id: int,
           db: Session = Depends(get_db)):
  return db_techniciens.delete_tech(db, id)