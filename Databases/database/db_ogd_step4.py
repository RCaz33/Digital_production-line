from sqlalchemy.orm.session import Session
from schemas import Batch_OGDStep4_Base
from database.models import DbForm_S4
from fastapi import HTTPException, status
from database import db_techniciens, db_ogd_step0 

# CREATE

def create_batch_s4(db: Session, request: Batch_OGDStep4_Base):  # uses schema 

  batch_s0 = db_ogd_step0.get_batch_s0_by_batchname(db,request.Step4_BatchName)
  id = int(batch_s0.Batch_id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step4_Initiales)
  tech_id = int(tech.Technicien_id)

  new_batch = DbForm_S4(   # uses database
    Batch_id = id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    Date = request.Step4_Date,
    Technicien_id = tech_id,
    m_OGD = request.Step4_m_OGD,
    m_THF = request.Step4_m_THF,
    Abs_800 = request.Step4_Abs_800,
    QC_Conc_OGD = request.Step4_QC_Conc_OGD,
    QC_Categorie = request.Step4_QC_Categorie,
    Stockage_recipient = request.Step4_Stockage_recipient,
    Stockage_Emplacement = request.Step4_Stockage_Emplacement,
    Stockage_Utilisation = request.Step4_Stockage_Utilisation,
    Observations = request.Step4_Observations
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

def get_all_batch_s4(db: Session):
  return db.query(DbForm_S4).all()

def get_batch_s4(db: Session, id: int):
  batch_s4 = db.query(DbForm_S4).filter(DbForm_S4.Batch_id == id).first()
  if not batch_s4:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return batch_s4

def get_batch_s4_by_batchname(db: Session, batch_name: str):
  batch_s4 = db.query(DbForm_S4).filter(DbForm_S4.Batch_id == id).first()
  if not batch_s4:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with name {batch_name} not found')
  return batch_s4


# UPDATE

def update_batch_s4(db: Session, id: int, request: Batch_OGDStep4_Base):
  batch_s4 = db.query(DbForm_S4).filter(DbForm_S4.Batch_id == id)
  tech = db_techniciens.get_tech_by_initials(db,request.Step4_Initiales)
  tech_id = int(tech.Technicien_id)
  if not batch_s4.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  batch_s4.update({  # uses database
    DbForm_S4.Batch_id : id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DbForm_S4.Date : request.Step4_Date,
    DbForm_S4.Technicien_id : tech_id,
    DbForm_S4.m_OGD : request.Step4_m_OGD,
    DbForm_S4.m_THF : request.Step4_m_THF,
    DbForm_S4.Abs_800 : request.Step4_Abs_800,
    DbForm_S4.QC_Conc_OGD : request.Step4_QC_Conc_OGD,
    DbForm_S4.QC_Categorie : request.Step4_QC_Categorie,
    DbForm_S4.Stockage_recipient : request.Step4_Stockage_recipient,
    DbForm_S4.Stockage_Emplacement : request.Step4_Stockage_Emplacement,
    DbForm_S4.Stockage_Utilisation : request.Step4_Stockage_Utilisation,
    DbForm_S4.Observations : request.Step4_Observations,
})
  db.commit()
  return 'ok'


# DELETE

def delete_user_s4(db: Session, id: int):
  batch_s4 = db.query(DbForm_S4).filter(DbForm_S4.Batch_id == id).first()
  if not batch_s4:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(batch_s4)
  db.commit()
  return 'ok'