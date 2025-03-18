from sqlalchemy.orm.session import Session
from app.schemas import Client_Base, Client_Add
from app.database.models import DB_Client
from fastapi import HTTPException, status

# CREATE

def create_Client(db: Session, request: Client_Add):  # uses schema 

#   s0 = db_Client_step0.get_s0_byname(db,request.Step1Name)
#   id = int(s0.Client_id)
#   tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
#   tech_id = int(tech.Technicien_id)

    new = DB_Client(   # uses database
        Client_nom = request.Client_nom,
        Client_adresse = request.Client_adresse,)

    try:
        db.add(new)
        db.commit()
        db.refresh(new)
        return new
    
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                                detail=f"This batch already registered (error{e})")


# READ 

def get_all_Client(db: Session):
    return db.query(DB_Client).all()

def get_Client(db: Session, id: int):
    Client = db.query(DB_Client).filter(DB_Client.Client_id == id).first()
    if not Client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Batch with id {id} not found')
    return Client

def get_Client_by_produit_name(db: Session, produit_name: str):
    Client = db.query(DB_Client).filter(DB_Client.Client_produit_name == produit_name).first()
    if not Client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Batch with name {produit_name} not found')
    return Client


# UPDATE

def update_Client(db: Session, id: int, request: Client_Base):
    Client = db.query(DB_Client).filter(DB_Client.Client_id == id)
    # tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
    # tech_id = int(tech.Technicien_id)
    # if not Client.first():
    #   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #     detail=f'User with id {id} not found')
    Client.update({  # uses database
        DB_Client.Client_id : id,  #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
        DB_Client.Client_nom : request.Client_nom,
        DB_Client.Client_adresse : request.Client_adresse})
    
    db.commit()
    return 'ok'


# DELETE

def delete_Client(db: Session, id: int):
    Client = db.query(DB_Client).filter(DB_Client.Client_id == id).first()
    if not Client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {id} not found')
    db.delete(Client)
    db.commit()
    return 'ok'