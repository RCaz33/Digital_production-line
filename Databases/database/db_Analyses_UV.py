from sqlalchemy.orm.session import Session
from schemas import Analyses_UV_Base, Analyses_UV_Add
from database.models import DB_Analyses_UV
from fastapi import HTTPException, status

from database import db_techniciens, db_Analyses

# CREATE

def create_analyse_UV(db: Session, request: Analyses_UV_Add):  # uses schema 

  new_analyse = DB_Analyses_UV(   # uses database
    # Analyses_id = request.Analyses_id, # AUTO-INCREMENT
    Analyse_UV_name = request.Analyse_UV_name,
    Analyse_UV_subname = request.Analyse_UV_subname,
    Analyse_UV_details = request.Analyse_UV_details,
    Analyses_UV_data = request.Analyses_UV_data
    )

  try:
    db.add(new_analyse)
    db.commit()
    db.refresh(new_analyse)
    return new_analyse
  
  except Exception as e :
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"This batch already registered (error{e})")


# READ 

def get_all_analyses_UV(db: Session):
  return db.query(DB_Analyses_UV).all()

def get_analyse_id_UV(db: Session, id: int):
  Analyses = db.query(DB_Analyses_UV).filter(DB_Analyses_UV.Analyses_UV_id == id).first()
  if not Analyses:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Analyse with id {id} not found')
  return Analyses

def get_analyse_UV_by_name(db: Session, name: str):
  Analyses = db.query(DB_Analyses_UV).filter(DB_Analyses_UV.Analyse_UV_name == name).first()
  if not Analyses:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Analyse with code {name} not found')
  return Analyses


# UPDATE

def update_analyse_UV(db: Session, id: int, request: Analyses_UV_Base):
  Analyses = db.query(DB_Analyses_UV).filter(DB_Analyses_UV.Analyses_UV_id == id)


  if not Analyses.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  Analyses.update({  # uses database
    DB_Analyses_UV.Analyses_UV_id : request.Analyses_UV_id,
    DB_Analyses_UV.Analyse_UV_name : request.Analyse_UV_name,
    DB_Analyses_UV.Analyse_UV_subname : request.Analyse_UV_subname,
    DB_Analyses_UV.Analyse_UV_details : request.Analyse_UV_details,
    DB_Analyses_UV.Analyses_UV_data : request.Analyses_UV_data})
  db.commit()
  return 'ok'


# DELETE

def delete_analyse_UV(db: Session, id: int):
  Analyses = db.query(DB_Analyses_UV).filter(DB_Analyses_UV.Analyses_id == id).first()
  if not Analyses:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(Analyses)
  db.commit()
  return 'ok'