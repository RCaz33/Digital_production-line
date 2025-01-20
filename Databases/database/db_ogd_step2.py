from sqlalchemy.orm.session import Session
from schemas import Batch_OGDstep2_Base
from database.models import DbForm_S2
from fastapi import HTTPException, status
from database import db_techniciens, db_ogd_step0 

# CREATE

def create_batch_s2(db: Session, request: Batch_OGDstep2_Base):  # uses schema 

  batch_s0 = db_ogd_step0.get_batch_s0_by_batchname(db,request.Step2_BatchName)
  id = int(batch_s0.Batch_id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step2_Initiales)
  tech_id = int(tech.Technicien_id)

  new_batch = DbForm_S2(   # uses database
    Batch_id = id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    Date = request.Step2_Date,
    Technicien_id = tech_id,
    Ajout_THF_JourJ = request.Step2_Ajout_THF_JourJ,
    Heure_ajout2 = request.Step2_Heure_ajout2,
    Volume_THF_ajout2 = request.Step2_Volume_THF_ajout2,
    Heure_debut_sedimentation = request.Step2_Heure_debut_sedimentation,
    Heure_fin_sedimentation =request.Step2_Heure_fin_sedimentation,
    Sediments = request.Step2_Sediments,
    Ctrl_visuel_couleur = request.Step2_Ctrl_visuel_couleur,
    Lab_HR = request.Step2_env_Lab_H2O,
    Lab_T = request.Step2_env_Lab_T,
    BaG_T = request.Step2_env_GloveBox_T,
    BaG_H2O_ppm = request.Step2_env_GloveBox_H2O,
    BaG_O2_ppm = request.Step2_env_GloveBox_O2,
    Observations = request.Step2_Observation,
    Centrifugation = request.Step2_Centrifugation
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

def get_all_batch_s2(db: Session):
  return db.query(DbForm_S2).all()

def get_batch_s2(db: Session, id: int):
  batch_s2 = db.query(DbForm_S2).filter(DbForm_S2.Batch_id == id).first()
  if not batch_s2:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return batch_s2

def get_batch_s2_by_batchname(db: Session, batch_name: str):
  batch_s2 = db.query(DbForm_S2).filter(DbForm_S2.Batch_id == id).first()
  if not batch_s2:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return batch_s2


# UPDATE

def update_batch_s2(db: Session, id: int, request: Batch_OGDstep2_Base):
  batch_s2 = db.query(DbForm_S2).filter(DbForm_S2.Batch_id == id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step2_Initiales)
  tech_id = int(tech.Technicien_id)
  if not batch_s2.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  batch_s2.update({  # uses database
    DbForm_S2.Batch_id : id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DbForm_S2.Date : request.Step1_Date,
    DbForm_S2.Technicien_id : tech_id,
    DbForm_S2.Ajout_THF_JourJ : request.Step2_Ajout_THF_JourJ,
    DbForm_S2.Heure_ajout2 : request.Step2_Heure_ajout2,
    DbForm_S2.Volume_THF_ajout2 : request.Step2_Volume_THF_ajout2,
    DbForm_S2.Heure_debut_sedimentation : request.Step2_Heure_debut_sedimentation,
    DbForm_S2.Heure_fin_sedimentation : request.Step2_Heure_fin_sedimentation,
    DbForm_S2.Sediments : request.Step2_Sediments,
    DbForm_S2.Ctrl_visuel_couleur : request.Step2_Ctrl_visuel_couleur,
    DbForm_S2.Lab_HR : request.Step2_env_Lab_H2O,
    DbForm_S2.Lab_T : request.Step2_env_Lab_T,
    DbForm_S2.BaG_T : request.Step2_env_GloveBox_T,
    DbForm_S2.BaG_H2O_ppm : request.Step2_env_GloveBox_H2O,
    DbForm_S2.BaG_O2_ppm : request.Step2_env_GloveBox_O2,
    DbForm_S2.Observations : request.Step2_Observation,
    DbForm_S2.Centrifugation : request.Step2_Centrifugation}
  )
  db.commit()
  return 'ok'


# DELETE

def delete_user_s2(db: Session, id: int):
  batch_s2 = db.query(DbForm_S2).filter(DbForm_S2.Batch_id == id).first()
  if not batch_s2:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(batch_s2)
  db.commit()
  return 'ok'