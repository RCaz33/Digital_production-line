from sqlalchemy.orm.session import Session
from app.schemas import Batch_XY_Base, Batch_XY_Add
from app.database.models import DB_Batch_XY
from fastapi import HTTPException, status


# CREATE

def create_batch_XY(db: Session, request: Batch_XY_Add):  # uses schema 

#   batch_s0 = db_ogd_step0.get_batch_s0_by_batchname(db,request.Step1_BatchName)
#   id = int(batch_s0.Batch_XY_id)
#   tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
#   tech_id = int(tech.Technicien_id)

  new_batch = DB_Batch_XY(   # uses database
    # Batch_XY_id = request.Batch_XY_id, # AUTO-INCREMENT
    Batch_XY_name = request.Batch_XY_name,
    Batch_XY_date = request.Batch_XY_date,
    Batch_XY_Technicien = request.Batch_XY_Technicien,
    Batch_XY_KC8_batch = request.Batch_XY_KC8_batch,
    Batch_XY_KC8_masse = request.Batch_XY_KC8_masse,
    Batch_XY_YY_batch = request.Batch_XY_YY_batch,
    Batch_XY_YY_Volume = request.Batch_XY_YY_Volume,
    Batch_XY_Temperature = request.Batch_XY_Temperature,
    Batch_XY_Agitation = request.Batch_XY_Agitation,
    Batch_XY_heure_debut = request.Batch_XY_heure_debut,
    Batch_XY_heure_fin = request.Batch_XY_heure_fin,
    Batch_XY_room_HR = request.Batch_XY_room_HR,
    Batch_XY_room_T = request.Batch_XY_room_T,
    Batch_XY_Stock = request.Batch_XY_Stock,
    Batch_XY_Analyses = request.Batch_XY_Analyses)

  try:
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch
  
  except Exception as e :
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"This batch already registered (error{e})")


# READ 

def get_all_batch_XY(db: Session):
  return db.query(DB_Batch_XY).all()

def get_batch_XY(db: Session, id: int):
  batch_XY = db.query(DB_Batch_XY).filter(DB_Batch_XY.Batch_XY_id == id).first()
  if not batch_XY:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return batch_XY

def get_batch_XY_by_batchname(db: Session, batch_name: str):
  batch_XY = db.query(DB_Batch_XY).filter(DB_Batch_XY.Batch_XY_name == batch_name).first()
  if not batch_XY:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return batch_XY


# UPDATE

def update_batch_XY(db: Session, id: int, request: Batch_XY_Base):
  batch_XY = db.query(DB_Batch_XY).filter(DB_Batch_XY.Batch_XY_id == id)
  # tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
  # tech_id = int(tech.Technicien_id)
  # if not batch_XY.first():
  #   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
  #     detail=f'User with id {id} not found')
  batch_XY.update({  # uses database
    DB_Batch_XY.Batch_XY_id : id,  #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DB_Batch_XY.Batch_XY_name : request.Batch_XY_name,
    DB_Batch_XY.Batch_XY_date : request.Batch_XY_date,
    DB_Batch_XY.Batch_XY_Technicien : request.Batch_XY_Technicien,
    DB_Batch_XY.Batch_XY_KC8_batch : request.Batch_XY_KC8_batch,
    DB_Batch_XY.Batch_XY_KC8_masse : request.Batch_XY_KC8_masse,
    DB_Batch_XY.Batch_XY_YY_batch : request.Batch_XY_YY_batch,
    DB_Batch_XY.Batch_XY_YY_Volume : request.Batch_XY_YY_Volume,
    DB_Batch_XY.Batch_XY_Temperature : request.Batch_XY_Temperature,
    DB_Batch_XY.Batch_XY_Agitation : request.Batch_XY_Agitation,
    DB_Batch_XY.Batch_XY_heure_debut : request.Batch_XY_heure_debut,
    DB_Batch_XY.Batch_XY_heure_fin : request.Batch_XY_heure_fin,
    DB_Batch_XY.Batch_XY_room_HR : request.Batch_XY_room_HR,
    DB_Batch_XY.Batch_XY_room_T : request.Batch_XY_room_T,
    DB_Batch_XY.Batch_XY_Stock : request.Batch_XY_Stock,
    DB_Batch_XY.Batch_XY_Analyses : request.Batch_XY_Analyses})
  
  db.commit()
  return 'ok'


# DELETE

def delete_batch_XY(db: Session, id: int):
  batch_XY = db.query(DB_Batch_XY).filter(DB_Batch_XY.Batch_XY_id == id).first()
  if not batch_XY:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(batch_XY)
  db.commit()
  return 'ok'