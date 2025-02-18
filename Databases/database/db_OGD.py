from sqlalchemy.orm.session import Session
from schemas import Batch_OGD_Base, Batch_OGD_Add
from database.models import DB_Batch_OGD
from fastapi import HTTPException, status

from database import db_techniciens, db_OGD

# CREATE

def create_batch_OGD(db: Session, request: Batch_OGD_Add):  # uses schema 

#   batch_s0 = db_ogd_step0.get_batch_s0_by_batchname(db,request.Step1_BatchName)
#   id = int(batch_s0.Batch_OGD_id)
#   tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
#   tech_id = int(tech.Technicien_id)

  new_batch = DB_Batch_OGD(   # uses database
    # Batch_OGD_id = request.Batch_OGD_id, # AUTO-INCREMENT
    Batch_OGD_name = request.Batch_OGD_name,
    Batch_OGD_date = request.Batch_OGD_date,
    Batch_OGD_Technicien = request.Batch_OGD_Technicien,
    Batch_OGD_KC8_batch = request.Batch_OGD_KC8_batch,
    Batch_OGD_KC8_masse = request.Batch_OGD_KC8_masse,
    Batch_OGD_THF_batch = request.Batch_OGD_THF_batch,
    Batch_OGD_THF_Volume = request.Batch_OGD_THF_Volume,
    Batch_OGD_Temperature = request.Batch_OGD_Temperature,
    Batch_OGD_Agitation = request.Batch_OGD_Agitation,
    Batch_OGD_heure_debut = request.Batch_OGD_heure_debut,
    Batch_OGD_heure_fin = request.Batch_OGD_heure_fin,
    Batch_OGD_room_HR = request.Batch_OGD_room_HR,
    Batch_OGD_room_T = request.Batch_OGD_room_T,
    Batch_OGD_Stock = request.Batch_OGD_Stock,
    Batch_OGD_Analyses = request.Batch_OGD_Analyses)

  try:
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch
  
  except Exception as e :
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"This batch already registered (error{e})")


# READ 

def get_all_batch_OGD(db: Session):
  return db.query(DB_Batch_OGD).all()

def get_batch_OGD(db: Session, id: int):
  batch_OGD = db.query(DB_Batch_OGD).filter(DB_Batch_OGD.Batch_OGD_id == id).first()
  if not batch_OGD:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return batch_OGD

def get_batch_OGD_by_batchname(db: Session, batch_name: str):
  batch_OGD = db.query(DB_Batch_OGD).filter(DB_Batch_OGD.Batch_OGD_name == batch_name).first()
  if not batch_OGD:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return batch_OGD


# UPDATE

def update_batch_OGD(db: Session, id: int, request: Batch_OGD_Base):
  batch_OGD = db.query(DB_Batch_OGD).filter(DB_Batch_OGD.Batch_OGD_id == id)
  # tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
  # tech_id = int(tech.Technicien_id)
  # if not batch_OGD.first():
  #   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
  #     detail=f'User with id {id} not found')
  batch_OGD.update({  # uses database
    DB_Batch_OGD.Batch_OGD_id : id,  #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DB_Batch_OGD.Batch_OGD_name : request.Batch_OGD_name,
    DB_Batch_OGD.Batch_OGD_date : request.Batch_OGD_date,
    DB_Batch_OGD.Batch_OGD_Technicien : request.Batch_OGD_Technicien,
    DB_Batch_OGD.Batch_OGD_KC8_batch : request.Batch_OGD_KC8_batch,
    DB_Batch_OGD.Batch_OGD_KC8_masse : request.Batch_OGD_KC8_masse,
    DB_Batch_OGD.Batch_OGD_THF_batch : request.Batch_OGD_THF_batch,
    DB_Batch_OGD.Batch_OGD_THF_Volume : request.Batch_OGD_THF_Volume,
    DB_Batch_OGD.Batch_OGD_Temperature : request.Batch_OGD_Temperature,
    DB_Batch_OGD.Batch_OGD_Agitation : request.Batch_OGD_Agitation,
    DB_Batch_OGD.Batch_OGD_heure_debut : request.Batch_OGD_heure_debut,
    DB_Batch_OGD.Batch_OGD_heure_fin : request.Batch_OGD_heure_fin,
    DB_Batch_OGD.Batch_OGD_room_HR : request.Batch_OGD_room_HR,
    DB_Batch_OGD.Batch_OGD_room_T : request.Batch_OGD_room_T,
    DB_Batch_OGD.Batch_OGD_Stock : request.Batch_OGD_Stock,
    DB_Batch_OGD.Batch_OGD_Analyses : request.Batch_OGD_Analyses})
  
  db.commit()
  return 'ok'


# DELETE

def delete_batch_OGD(db: Session, id: int):
  batch_OGD = db.query(DB_Batch_OGD).filter(DB_Batch_OGD.Batch_OGD_id == id).first()
  if not batch_OGD:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(batch_OGD)
  db.commit()
  return 'ok'