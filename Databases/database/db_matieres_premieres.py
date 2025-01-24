from sqlalchemy.orm.session import Session
from schemas import Matieres_premieres_Base, Matieres_premieres_Add
from database.models import DB_Matieres_premieres
from fastapi import HTTPException, status

from database import db_techniciens, db_matieres_premieres

# CREATE

def create_matieres_premieres(db: Session, request: Matieres_premieres_Add):  # uses schema 

  new_matieres_premieres = DB_Matieres_premieres( 
    MP_nom = request.MP_nom,
    MP_codeCW = request.MP_codeCW,
    MP_ref_fournisseur = request.MP_ref_fournisseur,
    MP_date_reception = request.MP_date_reception,
    MP_quantite = request.MP_quantite,
    MP_unite = request.MP_unite,
    MP_Analyses = request.MP_Analyses
)

  try:
    db.add(new_matieres_premieres)
    db.commit()
    db.refresh(new_matieres_premieres)
    return new_matieres_premieres
  
  except Exception as e :
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"This batch already registered (error{e})")


# READ 

def get_all_matieres_premieres(db: Session):
  return db.query(DB_Matieres_premieres).all()

def get_matieres_premieres(db: Session, id: int):
  matieres_premieress = db.query(DB_Matieres_premieres).filter(DB_Matieres_premieres.MP_id == id).first()
  if not matieres_premieress:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'matieres_premieres with id {id} not found')
  return matieres_premieress

def get_matieres_premieres_by_ref(db: Session, ref_matieres_premieres: str):
  matieres_premieress = db.query(DB_Matieres_premieres).filter(DB_Matieres_premieres.MP_ref_fournisseur == ref_matieres_premieres).first()
  if not matieres_premieress:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'matieres_premieres with code {ref_matieres_premieres} not found')
  return matieres_premieress

def get_matieres_premieres_by_code(db: Session, code_matieres_premieres: str):
  matieres_premieress = db.query(DB_Matieres_premieres).filter(DB_Matieres_premieres.MP_codeCW == code_matieres_premieres).first()
  if not matieres_premieress:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'matieres_premieres with code {code_matieres_premieres} not found')
  return matieres_premieress


# UPDATE

def update_matieres_premieres(db: Session, id: int, request: Matieres_premieres_Base):
  matieres_premieress = db.query(DB_Matieres_premieres).filter(DB_Matieres_premieres.MP_id == id)


  if not matieres_premieress.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  matieres_premieress.update({  # uses database
    DB_Matieres_premieres.MP_id : request.MP_id,
    DB_Matieres_premieres.MP_nom : request.MP_nom,
    DB_Matieres_premieres.MP_codeCW : request.MP_codeCW,
    DB_Matieres_premieres.MP_ref_fournisseur : request.MP_ref_fournisseur,
    DB_Matieres_premieres.MP_date_reception : request.MP_date_reception,
    DB_Matieres_premieres.MP_quantite : request.MP_quantite,
    DB_Matieres_premieres.MP_unite : request.MP_unite,
    DB_Matieres_premieres.MP_Analyses : request.MP_Analyses})
  db.commit()
  return 'ok'


# DELETE

def delete_matieres_premieres(db: Session, id: int):
  matieres_premieress = db.query(DB_Matieres_premieres).filter(DB_Matieres_premieres.MP_id == id).first()
  if not matieres_premieress:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(matieres_premieress)
  db.commit()
  return 'ok'