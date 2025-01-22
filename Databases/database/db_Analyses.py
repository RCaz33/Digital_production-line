from sqlalchemy.orm.session import Session
from schemas import Analyses_Base, Analyses_Base_Add
from database.models import DB_Analyses
from fastapi import HTTPException, status

from database import db_techniciens, db_Analyses

# CREATE

def create_analyse(db: Session, request: Analyses_Base_Add):  # uses schema 

  new_analyse = DB_Analyses(   # uses database
    # Analyses_id = request.Analyses_id, # AUTO-INCREMENT
    Analyse_path_to_raw = request.Analyse_path_to_raw,
    Analyse_code = request.Analyse_code,
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

def get_analyse(db: Session, id: int):
  Analyses = db.query(DB_Analyses).filter(DB_Analyses.Analyses_id == id).first()
  if not Analyses:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Analyse with id {id} not found')
  return Analyses

def get_analyse_by_code(db: Session, code_analyse: str):
  Analyses = db.query(DB_Analyses).filter(DB_Analyses.Analyse_code == code_analyse).first()
  if not Analyses:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Analyse with code {code_analyse} not found')
  return Analyses


# UPDATE

def update_analyse(db: Session, id: int, request: Analyses_Base):
  Analyses = db.query(DB_Analyses).filter(DB_Analyses.Analyses_id == id)


  if not Analyses.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  Analyses.update({  # uses database
    DB_Analyses.Analyses_id : request.Analyses_id,
    DB_Analyses.Analyse_path_to_raw : request.Analyse_path_to_raw,
    DB_Analyses.Analyse_code : request.Analyse_code})
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