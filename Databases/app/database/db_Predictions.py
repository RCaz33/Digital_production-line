from sqlalchemy.orm.session import Session
from app.schemas import Prediction_Base, Prediction_Add
from app.database.models import DB_Prediction
from fastapi import HTTPException, status

# CREATE

def create_prediction(db: Session, request: Prediction_Add):  # uses schema 

    new = DB_Prediction(   # uses database
        Prediction_date = request.Prediction_date,
        Prediction_type = request.Prediction_type,
        Prediction_model_version = request.Prediction_model_version,
        Prediction_data = request.Prediction_data)

    try:
        db.add(new)
        db.commit()
        db.refresh(new)
        return new
    
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                                detail=f"This prediction already exist (error{e})")


# READ 

def get_all_Prediction(db: Session):
    return db.query(DB_Prediction).all()

def get_Prediction(db: Session, id: int):
    Prediction = db.query(DB_Prediction).filter(DB_Prediction.Prediction_id == id).first()
    if not Prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Batch with id {id} not found')
    return Prediction

def get_Prediction_by_type(db: Session, type_prediction: str):
    Prediction = db.query(DB_Prediction).filter(DB_Prediction.Prediction_type == type_prediction).first()
    if not Prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Batch with name {type_prediction} not found')
    return Prediction


# UPDATE

def update_Prediction(db: Session, id: int, request: Prediction_Base):
    Prediction = db.query(DB_Prediction).filter(DB_Prediction.Prediction_id == id)

    Prediction.update({  # uses database
        DB_Prediction.Prediction_id : id,  #### ATTENTION, PEUT ETRE BESOIN IDENTIFIER
        DB_Prediction.Prediction_date : request.Prediction_date,
        DB_Prediction.Prediction_type : request.Prediction_type,
        DB_Prediction.Prediction_model_version : request.Prediction_model_version,
        DB_Prediction.Prediction_data : request.Prediction_data})
    
    db.commit()
    return 'ok'


# DELETE

def delete_Prediction(db: Session, id: int):
    Prediction = db.query(DB_Prediction).filter(DB_Prediction.Prediction_id == id).first()
    if not Prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User with id {id} not found')
    db.delete(Prediction)
    db.commit()
    return 'ok'