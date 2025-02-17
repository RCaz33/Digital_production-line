from sqlalchemy.orm.session import Session
from schemas import Analyses_Base, Analyses_Add
from database.models import DB_Analyses
from fastapi import HTTPException, status

from database import db_techniciens, db_Analyses

# CREATE

def create_analyse(db: Session, request: Analyses_Add):  # uses schema 

  new_analyse = DB_Analyses(   # uses database
    # Analyses_id = request.Analyses_id, # AUTO-INCREMENT
    Analyse_name = request.Analyse_name,
    Analyse_subname = request.Analyse_subname,
    Analyse_details = request.Analyse_details,
    Analyses_data = request.Analyses_data
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

def get_all_analyses(db: Session):
  return db.query(DB_Analyses).all()

def get_analyse_id(db: Session, id: int):
  Analyses = db.query(DB_Analyses).filter(DB_Analyses.Analyses_id == id).first()
  if not Analyses:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Analyse with id {id} not found')
  return Analyses

def get_analyse_by_name(db: Session, name: str):
  Analyses = db.query(DB_Analyses).filter(DB_Analyses.Analyse_name == name)
  if not Analyses:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Analyse with code {name} not found')
  return Analyses


# UPDATE

def update_analyse(db: Session, id: int, request: Analyses_Base):
  Analyses = db.query(DB_Analyses).filter(DB_Analyses.Analyses_id == id)


  if not Analyses.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  Analyses.update({  # uses database
    DB_Analyses.Analyses_id : request.Analyses_id,
    DB_Analyses.Analyse_name : request.Analyse_name,
    DB_Analyses.Analyse_subname : request.Analyse_subname,
    DB_Analyses.Analyse_details : request.Analyse_details,
    DB_Analyses.Analyses_data : request.Analyses_data})
  db.commit()
  return 'ok'


# DELETE

def delete_analyse(db: Session, id: int):
  Analyses = db.query(DB_Analyses).filter(DB_Analyses.Analyses_id == id).first()
  if not Analyses:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(Analyses)
  db.commit()
  return 'ok'