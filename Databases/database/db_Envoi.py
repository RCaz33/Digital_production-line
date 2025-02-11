from sqlalchemy.orm.session import Session
from schemas import Envoi_Base, Envoi_Add
from database.models import DB_Envoi
from fastapi import HTTPException, status
from database import db_techniciens, db_Envoi

# CREATE

def create_Envoi(db: Session, request: Envoi_Add):  # uses schema 

#   s0 = db_Envoi_step0.get_s0_byname(db,request.Step1Name)
#   id = int(s0.Envoi_id)
#   tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
#   tech_id = int(tech.Technicien_id)

    new = DB_Envoi(   # uses database
        Envoi_date_commande = request.Envoi_date_commande,
        Envoi_client_name = request.Envoi_client_name,
        Envoi_produit_name = request.Envoi_produit_name,
        Envoi_produit_batch = request.Envoi_produit_batch,
        Envoi_produit_Qte = request.Envoi_produit_Qte,
        Envoi_produit_emballage = request.Envoi_produit_emballage,
        Envoi_date_prevu = request.Envoi_date_prevu,
        Envoi_date_effective = request.Envoi_date_effective,
        Envoi_code_coli = request.Envoi_code_coli,
        Envoi_delivered = request.Envoi_delivered,
        Envoi_retour_client = request.Envoi_retour_client,)

    try:
        db.add(new)
        db.commit()
        db.refresh(new)
        return new
    
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                                detail=f"This batch already registered (error{e})")


# READ 

def get_all_Envoi(db: Session):
    return db.query(DB_Envoi).all()

def get_Envoi(db: Session, id: int):
    Envoi = db.query(DB_Envoi).filter(DB_Envoi.Envoi_id == id).first()
    if not Envoi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Batch with id {id} not found')
    return Envoi

def get_Envoi_by_produit_name(db: Session, produit_name: str):
    Envoi = db.query(DB_Envoi).filter(DB_Envoi.Envoi_produit_name == produit_name).first()
    if not Envoi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Batch with name {produit_name} not found')
    return Envoi


# UPDATE

def update_Envoi(db: Session, id: int, request: Envoi_Base):
    Envoi = db.query(DB_Envoi).filter(DB_Envoi.Envoi_id == id)
    # tech = db_techniciens.get_tech_by_initials(db,request.Step1_Initiales)
    # tech_id = int(tech.Technicien_id)
    # if not Envoi.first():
    #   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #     detail=f'User with id {id} not found')
    Envoi.update({  # uses database
        DB_Envoi.Envoi_id : id,  #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
        DB_Envoi.Envoi_date_commande : request.Envoi_date_commande,
        DB_Envoi.Envoi_client_name : request.Envoi_client_name,
        DB_Envoi.Envoi_produit_name : request.Envoi_produit_name,
        DB_Envoi.Envoi_produit_batch : request.Envoi_produit_batch,
        DB_Envoi.Envoi_produit_Qte : request.Envoi_produit_Qte,
        DB_Envoi.Envoi_produit_emballage : request.Envoi_produit_emballage,
        DB_Envoi.Envoi_date_prevu : request.Envoi_date_prevu,
        DB_Envoi.Envoi_date_effective : request.Envoi_date_effective,
        DB_Envoi.Envoi_code_coli : request.Envoi_code_coli,
        DB_Envoi.Envoi_delivered : request.Envoi_delivered,
        DB_Envoi.Envoi_retour_client : request.Envoi_retour_client})
    
    db.commit()
    return 'ok'


# DELETE

def delete_Envoi(db: Session, id: int):
    Envoi = db.query(DB_Envoi).filter(DB_Envoi.Envoi_id == id).first()
    if not Envoi:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {id} not found')
    db.delete(Envoi)
    db.commit()
    return 'ok'