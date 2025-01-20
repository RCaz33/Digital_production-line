from sqlalchemy.orm.session import Session
from schemas import Batch_OGDStep3_Base
from database.models import DbForm_S3
from fastapi import HTTPException, status
from database import db_techniciens, db_ogd_step0 

# CREATE

def create_batch_s3(db: Session, request: Batch_OGDStep3_Base):  # uses schema 

  batch_s0 = db_ogd_step0.get_batch_s0_by_batchname(db,request.Step3_BatchName)
  id = int(batch_s0.Batch_id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step3_Initiales)
  tech_id = int(tech.Technicien_id)

  new_batch = DbForm_S3(   # uses database
    Batch_id = id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    Date = request.Step3_Date,
    Technicien_id = tech_id,
    Debit_air_synthetique = request.Step3_Debit_air_synthetique,
    Temps_oxidation = request.Step3_Temps_oxidation,
    Lab_HR = request.Step2_env_Lab_H2O,
    Lab_T = request.Step2_env_Lab_T,
    Observations = request.Step3_Observations
  )

  try:
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch
  
  except Exception as e :
    # raise e # use to debug
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="This batch already registered")


# READ 

def get_all_batch_s3(db: Session):
  return db.query(DbForm_S3).all()

def get_batch_s3(db: Session, id: int):
  batch_s3 = db.query(DbForm_S3).filter(DbForm_S3.Batch_id == id).first()
  if not batch_s3:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return batch_s3

def get_batch_s3_by_batchname(db: Session, batch_name: str):
  batch_s3 = db.query(DbForm_S3).filter(DbForm_S3.Batch_id == id).first()
  if not batch_s3:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return batch_s3


# UPDATE

def update_batch_s3(db: Session, id: int, request: Batch_OGDStep3_Base):
  batch_s3 = db.query(DbForm_S3).filter(DbForm_S3.Batch_id == id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step3_Initiales)
  tech_id = int(tech.Technicien_id)
  if not batch_s3.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  batch_s3.update({  # uses database
    DbForm_S3.Batch_id : id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DbForm_S3.Date : request.Step3_Date,
    DbForm_S3.Technicien_id : tech_id,
    DbForm_S3.Debit_air_synthetique : request.Step3_Debit_air_synthetique,
    DbForm_S3.Temps_oxidation : request.Step3_Temps_oxidation,
    DbForm_S3.Lab_HR : request.Step3_env_Lab_H2O,
    DbForm_S3.Lab_T : request.Step3_env_Lab_T,
    DbForm_S3.Observations : request.Step3_Observations,
}
  )
  db.commit()
  return 'ok'


# DELETE

def delete_user_s3(db: Session, id: int):
  batch_s3 = db.query(DbForm_S3).filter(DbForm_S3.Batch_id == id).first()
  if not batch_s3:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(batch_s3)
  db.commit()
  return 'ok'