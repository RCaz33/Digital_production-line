from sqlalchemy.orm.session import Session
from schemas import Batch_OGDstep1_Base
from database.models import DbForm_S1
from fastapi import HTTPException, status

from database import db_techniciens, db_ogd_step0 

# CREATE

def create_batch_s1(db: Session, request: Batch_OGDstep1_Base):  # uses schema 

  batch_s0 = db_ogd_step0.get_batch_s0_by_batchname(db,request.Step1_BatchName)
  id = int(batch_s0.Batch_id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
  tech_id = int(tech.Technicien_id)

  new_batch = DbForm_S1(   # uses database
    Batch_id = id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    Date = request.Step1_Date,
    Technicien_id = tech_id,
    Batch_KC8 = request.Step1_KC8_Batch,
    Masse_KC8 = request.Step1_KC8_Masse,
    Volume_THF = request.Step1_KC8_VTHF,
    Ref_plaque = request.Step1_Exfoliation_RefPlaque,
    Vitesse_agitation =request.Step1_Exfoliation_Vitesse,
    Heure_debut = request.Step1_Exfoliation_Heure,
    Lab_HR = request.Step1_env_Lab_H2O,
    Lab_T = request.Step1_env_Lab_T,
    BaG_T = request.Step1_env_GloveBox_T,
    BaG_H2O_ppm = request.Step1_env_GloveBox_H2O,
    BaG_O2_ppm = request.Step1_env_GloveBox_O2,
    Observations = request.Step1_Observation
  )

  try:
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch
  
  except Exception as e :
    raise e # use to debug
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="This batch already registered")


# READ 

def get_all_batch_s1(db: Session):
  return db.query(DbForm_S1).all()

def get_batch_s1(db: Session, id: int):
  batch_s1 = db.query(DbForm_S1).filter(DbForm_S1.Batch_id == id).first()
  if not batch_s1:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return batch_s1

def get_batch_s1_by_batchname(db: Session, batch_name: str):



  batch_s1 = db.query(DbForm_S1).filter(DbForm_S1.Batch_id == id).first()
  if not batch_s1:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return batch_s1


# UPDATE

def update_batch_s1(db: Session, id: int, request: Batch_OGDstep1_Base):
  batch_s1 = db.query(DbForm_S1).filter(DbForm_S1.Batch_id == id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
  tech_id = int(tech.Technicien_id)
  if not batch_s1.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  batch_s1.update({  # uses database
    DbForm_S1.Batch_id : id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DbForm_S1.Date : request.Step1_Date,
    DbForm_S1.Technicien_id : tech_id,
    DbForm_S1.Batch_KC8 : request.Step1_KC8_Batch,
    DbForm_S1.Masse_KC8 : request.Step1_KC8_Masse,
    DbForm_S1.Volume_THF : request.Step1_KC8_VTHF,
    DbForm_S1.Ref_plaque : request.Step1_Exfoliation_RefPlaque,
    DbForm_S1.Vitesse_agitation :request.Step1_Exfoliation_Vitesse,
    DbForm_S1.Heure_debut : request.Step1_Exfoliation_Heure,
    DbForm_S1.Lab_HR : request.Step1_env_Lab_H2O,
    DbForm_S1.Lab_T : request.Step1_env_Lab_T,
    DbForm_S1.BaG_T : request.Step1_env_GloveBox_T,
    DbForm_S1.BaG_H2O_ppm : request.Step1_env_GloveBox_H2O,
    DbForm_S1.BaG_O2_ppm : request.Step1_env_GloveBox_O2,
    DbForm_S1.Observations : request.Step1_Observation}
  )
  db.commit()
  return 'ok'


# DELETE

def delete_user_s1(db: Session, id: int):
  batch_s1 = db.query(DbForm_S1).filter(DbForm_S1.Batch_id == id).first()
  if not batch_s1:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(batch_s1)
  db.commit()
  return 'ok'