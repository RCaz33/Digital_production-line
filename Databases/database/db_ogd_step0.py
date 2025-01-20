from sqlalchemy.orm.session import Session
from schemas import Batch_OGDstep0_Base
from database.models import DbForm_S0
from fastapi import HTTPException, status


# CREATE

def create_batch_s0(db: Session, request: Batch_OGDstep0_Base):  # uses schema 


  new_batch = DbForm_S0(   # uses database
    Batch_name = request.Step0_BatchName,
    Batch_THF_ref = request.Step0_BatchTHF,

  )
  try:
    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    return new_batch
  
  except:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="This batch already registered")


# READ 

def get_all_batch_s0(db: Session):
  return db.query(DbForm_S0).all()

def get_batch_s0_by_id(db: Session, id: int):
  batch_s0 = db.query(DbForm_S0).filter(DbForm_S0.Batch_id == id).first()
  if not batch_s0:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch with id {id} not found')
  return batch_s0

def get_batch_s0_by_batchname(db: Session, batch_name: str):
  batch_s0 = db.query(DbForm_S0).filter(DbForm_S0.Batch_name == batch_name).first()
  if not batch_s0:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Batch name {batch_name} not found')
  return batch_s0


# UPDATE

def update_batch_s0(db: Session, id: int, request: Batch_OGDstep0_Base):
  batch_s0 = db.query(DbForm_S0).filter(DbForm_S0.Batch_id == id)
  if not batch_s0.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {batch_s0} not found')
  
  ## must have exact same name as in DbForm_S0 which interact with database
  batch_s0.update({  # uses database
    # DbForm_S0.Batch_id : id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DbForm_S0.Batch_name : request.Step0_BatchName,
    DbForm_S0.Batch_THF_ref : request.Step0_BatchTHF,
})
  db.commit()
  return 'ok'


# DELETE

def delete_batch_s0(db: Session, id: int):
  batch_s0 = db.query(DbForm_S0).filter(DbForm_S0.Batch_id == id).first()
  if not batch_s0:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'User with id {id} not found')
  db.delete(batch_s0)
  db.commit()
  return 'ok'