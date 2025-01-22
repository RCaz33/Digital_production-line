from sqlalchemy.orm.session import Session
from schemas import Batch_KC8_Base, Batch_KC8_Add
from database.models import DB_Batch_KC8
from fastapi import HTTPException, status

from database import db_techniciens, db_KC8 

# CREATE

def create_batch_KC8(db: Session, request: Batch_KC8_Add):  # uses schema 

#   batch_s0 = db_ogd_step0.get_batch_s0_by_batchname(db,request.Step1_BatchName)
#   id = int(batch_s0.Batch_KC8_id)
#   tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
#   tech_id = int(tech.Technicien_id)

  new_batch = DB_Batch_KC8(   # uses database
    Batch_KC8_name = request.Batch_KC8_name,
    Batch_KC8_date = request.Batch_KC8_date,
    Batch_KC8_Technicien = request.Batch_KC8_Technicien,
    Batch_KC8_K_batch = request.Batch_KC8_K_batch,
    Batch_KC8_C_batch = request.Batch_KC8_C_batch,
    Batch_KC8_masse = request.Batch_KC8_masse,
    Batch_KC8_Temperature = request.Batch_KC8_Temperature,
    Batch_KC8_Agitation = request.Batch_KC8_Agitation,
    Batch_KC8_heure_debut = request.Batch_KC8_heure_debut,
    Batch_KC8_heure_fin = request.Batch_KC8_heure_fin,
    Batch_KC8_room_HR = request.Batch_KC8_room_HR,
    Batch_KC8_room_T = request.Batch_KC8_room_T,
    Batch_KC8_Analyses = request.Batch_KC8_Analyses)

  try:
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch
  
  except Exception as e :
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"This batch already registered (error{e})")


# READ 

def get_all_batch_KC8(db: Session):
  return db.query(DB_Batch_KC8).all()

def get_batch_KC8(db: Session, id: int):
  Batch_KC8 = db.query(DB_Batch_KC8).filter(DB_Batch_KC8.Batch_KC8_id == id).first()
  if not Batch_KC8:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return Batch_KC8

def get_batch_KC8_by_batchname(db: Session, batch_name: str):
  Batch_KC8 = db.query(DB_Batch_KC8).filter(DB_Batch_KC8.Batch_KC8_name == batch_name).first()
  if not Batch_KC8:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return Batch_KC8


# UPDATE

def update_batch_KC8(db: Session, id: int, request: Batch_KC8_Base):
  Batch_KC8 = db.query(DB_Batch_KC8).filter(DB_Batch_KC8.Batch_KC8_id == id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
  tech_id = int(tech.Technicien_id)
  if not Batch_KC8.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  Batch_KC8.update({  # uses database
    DB_Batch_KC8.Batch_KC8_id : id,  #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DB_Batch_KC8.Batch_KC8_name : request.Batch_KC8_name,
    DB_Batch_KC8.Batch_KC8_date : request.Batch_KC8_date,
    DB_Batch_KC8.Batch_KC8_Technicien : request.Batch_KC8_Technicien,
    DB_Batch_KC8.Batch_KC8_K_batch : request.Batch_KC8_K_batch,
    DB_Batch_KC8.Batch_KC8_C_batch : request.Batch_KC8_C_batch,
    DB_Batch_KC8.Batch_KC8_masse : request.Batch_KC8_masse,
    DB_Batch_KC8.Batch_KC8_Temperature : request.Batch_KC8_Temperature,
    DB_Batch_KC8.Batch_KC8_Agitation : request.Batch_KC8_Agitation,
    DB_Batch_KC8.Batch_KC8_heure_debut : request.Batch_KC8_heure_debut,
    DB_Batch_KC8.Batch_KC8_heure_fin : request.Batch_KC8_heure_fin,
    DB_Batch_KC8.Batch_KC8_room_HR : request.Batch_KC8_room_HR,
    DB_Batch_KC8.Batch_KC8_room_T : request.Batch_KC8_room_T,
    DB_Batch_KC8.Batch_KC8_Analyses : request.Batch_KC8_Analyses})
  
  db.commit()
  return 'ok'


# DELETE

def delete_batch_KC8(db: Session, id: int):
  Batch_KC8 = db.query(DB_Batch_KC8).filter(DB_Batch_KC8.Batch_KC8_id == id).first()
  if not Batch_KC8:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(Batch_KC8)
  db.commit()
  return 'ok'