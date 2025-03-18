from sqlalchemy.orm.session import Session
from app.schemas import Batch_Produit_Base, Batch_Produit_Add
from app.database.models import DB_Batch_Produit
from fastapi import HTTPException, status


# CREATE

def create_batch_Produit(db: Session, request: Batch_Produit_Add):  # uses schema 

#   batch_s0 = db_Produit_step0.get_batch_s0_by_batchname(db,request.Step1_BatchName)
#   id = int(batch_s0.Batch_Produit_id)
#   tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
#   tech_id = int(tech.Technicien_id)

  new_batch = DB_Batch_Produit(   # uses database
    Batch_Produit_ref_CW = request.Batch_Produit_ref_CW,
    Batch_Produit_date = request.Batch_Produit_date,
    Batch_Produit_Technicien = request.Batch_Produit_Technicien,
    Batch_Produit_OGD_batch = request.Batch_Produit_OGD_batch,
    Batch_Produit_OGD_Qte = request.Batch_Produit_OGD_Qte,
    Batch_Produit_additif_batch = request.Batch_Produit_additif_batch,
    Batch_Produit_additif_Qte = request.Batch_Produit_additif_Qte,
    Batch_produit_stock = request.Batch_produit_stock,
    Batch_Produit_Analyses = request.Batch_Produit_Analyses)

  try:
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch
  
  except Exception as e :
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"This batch already registered (error{e})")


# READ 

def get_all_batch_Produit(db: Session):
  return db.query(DB_Batch_Produit).all()

def get_batch_Produit(db: Session, id: int):
  batch_Produit = db.query(DB_Batch_Produit).filter(DB_Batch_Produit.Batch_Produit_id == id).first()
  if not batch_Produit:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return batch_Produit

def get_batch_Produit_by_batchname(db: Session, batch_name: str):
  batch_Produit = db.query(DB_Batch_Produit).filter(DB_Batch_Produit.Batch_Produit_ref_CW == batch_name).first()
  if not batch_Produit:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return batch_Produit


# UPDATE

def update_batch_Produit(db: Session, id: int, request: Batch_Produit_Base):
  batch_Produit = db.query(DB_Batch_Produit).filter(DB_Batch_Produit.Batch_Produit_id == id)
  # tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
  # tech_id = int(tech.Technicien_id)
  # if not batch_Produit.first():
  #   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
  #     detail=f'User with id {id} not found')
  batch_Produit.update({  # uses database
    DB_Batch_Produit.Batch_Produit_id : id,  #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DB_Batch_Produit.Batch_Produit_ref_CW : request.Batch_Produit_ref_CW,
    DB_Batch_Produit.Batch_Produit_date : request.Batch_Produit_date,
    DB_Batch_Produit.Batch_Produit_Technicien : request.Batch_Produit_Technicien,
    DB_Batch_Produit.Batch_Produit_OGD_batch : request.Batch_Produit_OGD_batch,
    DB_Batch_Produit.Batch_Produit_OGD_Qte : request.Batch_Produit_OGD_Qte,
    DB_Batch_Produit.Batch_Produit_additif_batch : request.Batch_Produit_additif_batch,
    DB_Batch_Produit.Batch_Produit_additif_Qte : request.Batch_Produit_additif_Qte,
    DB_Batch_Produit.Batch_produit_stock : request.Batch_produit_stock,
    DB_Batch_Produit.Batch_Produit_Analyses : request.Batch_Produit_Analyses})
  
  db.commit()
  return 'ok'


# DELETE

def delete_batch_Produit(db: Session, id: int):
  batch_Produit = db.query(DB_Batch_Produit).filter(DB_Batch_Produit.Batch_Produit_id == id).first()
  if not batch_Produit:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(batch_Produit)
  db.commit()
  return 'ok'