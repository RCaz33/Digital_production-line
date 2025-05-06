from sqlalchemy.orm.session import Session
from app.schemas import Batch_XX_Base, Batch_XX_Add
from app.database.models import DB_Batch_XX
from fastapi import HTTPException, status

# CREATE

def create_batch_XX(db: Session, request: Batch_XX_Add):  # uses schema 

#   batch_s0 = db_ogd_step0.get_batch_s0_by_batchname(db,request.Step1_BatchName)
#   id = int(batch_s0.Batch_XX_id)
#   tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
#   tech_id = int(tech.Technicien_id)

  new_batch = DB_Batch_XX(   # uses database
    Batch_XX_name = request.Batch_XX_name,
    Batch_XX_date = request.Batch_XX_date,
    Batch_XX_Technicien = request.Batch_XX_Technicien,
    Batch_XX_K_batch = request.Batch_XX_K_batch,
    Batch_XX_C_batch = request.Batch_XX_C_batch,
    Batch_XX_masse = request.Batch_XX_masse,
    Batch_XX_Temperature = request.Batch_XX_Temperature,
    Batch_XX_Agitation = request.Batch_XX_Agitation,
    Batch_XX_heure_debut = request.Batch_XX_heure_debut,
    Batch_XX_heure_fin = request.Batch_XX_heure_fin,
    Batch_XX_room_HR = request.Batch_XX_room_HR,
    Batch_XX_room_T = request.Batch_XX_room_T,
    Batch_XX_Stock = request.Batch_XX_Stock,
    Batch_XX_Analyses = request.Batch_XX_Analyses)

  try:
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch
  
  except Exception as e :
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail=f"This batch already registered (error{e})")


# READ 

def get_all_batch_XX(db: Session):
  return db.query(DB_Batch_XX).all()

def get_last_batch_XX(db: Session):
  return db.query(DB_Batch_XX).order_by(DB_Batch_XX.Batch_XX_id.desc()).first()

def get_batch_XX(db: Session, id: int):
  Batch_XX = db.query(DB_Batch_XX).filter(DB_Batch_XX.Batch_XX_id == id).first()
  if not Batch_XX:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return Batch_XX

def get_batch_XX_by_batchname(db: Session, batch_name: str):
  Batch_XX = db.query(DB_Batch_XX).filter(DB_Batch_XX.Batch_XX_name == batch_name).first()
  if not Batch_XX:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return Batch_XX


# UPDATE

def update_batch_XX(db: Session, id: int, request: Batch_XX_Base):
  Batch_XX = db.query(DB_Batch_XX).filter(DB_Batch_XX.Batch_XX_id == id)
  # tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
  # tech_id = int(tech.Technicien_id)
  if not Batch_XX.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  Batch_XX.update({  # uses database
    DB_Batch_XX.Batch_XX_id : id,  #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DB_Batch_XX.Batch_XX_name : request.Batch_XX_name,
    DB_Batch_XX.Batch_XX_date : request.Batch_XX_date,
    DB_Batch_XX.Batch_XX_Technicien : request.Batch_XX_Technicien,
    DB_Batch_XX.Batch_XX_K_batch : request.Batch_XX_K_batch,
    DB_Batch_XX.Batch_XX_C_batch : request.Batch_XX_C_batch,
    DB_Batch_XX.Batch_XX_masse : request.Batch_XX_masse,
    DB_Batch_XX.Batch_XX_Temperature : request.Batch_XX_Temperature,
    DB_Batch_XX.Batch_XX_Agitation : request.Batch_XX_Agitation,
    DB_Batch_XX.Batch_XX_heure_debut : request.Batch_XX_heure_debut,
    DB_Batch_XX.Batch_XX_heure_fin : request.Batch_XX_heure_fin,
    DB_Batch_XX.Batch_XX_room_HR : request.Batch_XX_room_HR,
    DB_Batch_XX.Batch_XX_room_T : request.Batch_XX_room_T,
    DB_Batch_XX.Batch_XX_Stock : request.Batch_XX_Stock,
    DB_Batch_XX.Batch_XX_Analyses : request.Batch_XX_Analyses})
  
  db.commit()
  return 'ok'


# DELETE

def delete_batch_XX(db: Session, id: int):
  Batch_XX = db.query(DB_Batch_XX).filter(DB_Batch_XX.Batch_XX_id == id).first()
  if not Batch_XX:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(Batch_XX)
  db.commit()
  return 'ok'