from sqlalchemy.orm.session import Session
from app.schemas import Technicien_Base, Technicien_Create_record
from app.database.models import DbTechnicient
from fastapi import HTTPException, status


# CREATE


def create_technicien(db: Session, request: Technicien_Create_record):  # uses schema 
  Tech_ini = "".join([a[0].upper() for a in request.Tech_name.split(" ")])

  new_tech = DbTechnicient(   # uses database
    Initiales_tech = Tech_ini,
    Technicien_info_2 = request.Tech_name
  )
  try:
    db.add(new_tech)
    db.commit()
    db.refresh(new_tech)
    return new_tech
  
  except:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="This Technician is already registered")


# READ 
def get_all_tech(db: Session):
  return db.query(DbTechnicient).all()

def get_tech_by_id(db: Session, id: int):
  Tech = db.query(DbTechnicient).filter(DbTechnicient.Technicien_id == id).first()
  if not Tech:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Technician with id {id} not found')
  return Tech

def get_tech_by_initials(db: Session, initiales: str):
  batch_s0 = db.query(DbTechnicient).filter(DbTechnicient.Initiales_tech == initiales).first()
  if not batch_s0:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Technician name {initiales} not found')
  return batch_s0

# UPDATE

def update_tech(db: Session, id: int, request: Technicien_Base):
  tech = db.query(DbTechnicient).filter(DbTechnicient.Technicien_id == id)
  if not tech.first():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Technician with id {tech} not found')
  
  ## must have exact same name as in DbForm_S0 which interact with database
  tech.update({  # uses database
    # DbForm_S0.Batch_id : id,   #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
    DbTechnicient.Initiales_tech : request.Tech_ini,
    DbTechnicient.Technicien_info_2 : request.Tech_name,
})
  db.commit()
  return 'ok'



# DELETE
def delete_tech(db: Session, id: int):
  tech = db.query(DbTechnicient).filter(DbTechnicient.Technicien_id == id).first()
  if not tech:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
      detail=f'Technician with id {id} not found')
  db.delete(tech)
  db.commit()
  return 'ok'