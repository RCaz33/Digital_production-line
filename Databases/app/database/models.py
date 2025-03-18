from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Boolean, DateTime, Float, Time
from app.database.db_connect import Base
from sqlalchemy import Column, JSON





class DB_Prediction(Base):
    __tablename__ = 'Predictions'
    Prediction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Prediction_date = Column(DateTime, nullable=False)
    Prediction_type = Column(String(50), nullable=False)
    Prediction_model_version = Column(String(50), nullable=False)
    Prediction_data = Column(JSON, nullable=True)

class DB_Analyses(Base):
    __tablename__ = 'Analyses'
    Analyses_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Analyse_name = Column(String(50), nullable=False)
    Analyse_subname = Column(String(50), nullable=True) 
    Analyse_details = Column(JSON, nullable=True)
    Analyses_data = Column(JSON, nullable=True) # 'CodeEchantillon_date_type_details'


class DB_Matieres_premieres(Base):
    __tablename__ = 'Matieres_premieres'
    MP_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    MP_nom = Column(String(20), nullable=False)
    MP_codeCW = Column(String(10), nullable=False)
    MP_ref_fournisseur = Column(String(50), nullable=False)
    MP_date_reception = Column(DateTime, nullable=False)
    MP_quantite = Column(Float, default=20.0, nullable=False)
    MP_unite = Column(String(10), nullable=False)
    MP_Analyses = Column(String(50), nullable=True)
    MP_stock = Column(Float, default=0.0, nullable=False)
 # name of batch + date of analysis + type of analysis + details analysis
                      # "nom_250129_Raman / nom_250202_DLS / .."
 
class DB_Batch_KC8(Base):
    __tablename__ = 'Batch_KC8'
    Batch_KC8_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Batch_KC8_name = Column(String(10), nullable=False, unique=True)
    Batch_KC8_date = Column(DateTime, nullable=False)
    Batch_KC8_Technicien = Column(String(5), nullable=False)
    Batch_KC8_K_batch = Column(String(50), nullable=False)
    Batch_KC8_C_batch = Column(String(50), nullable=False)
    Batch_KC8_masse = Column(Float, nullable=False)
    Batch_KC8_Temperature = Column(Float, default=20.0, nullable=False)
    Batch_KC8_Agitation = Column(Integer, nullable=False)
    Batch_KC8_heure_debut = Column(DateTime, nullable=False)
    Batch_KC8_heure_fin = Column(DateTime, nullable=True)
    Batch_KC8_room_HR = Column(Float, default=20.0, nullable=False)
    Batch_KC8_room_T = Column(Float, default=20.0, nullable=False)
    Batch_KC8_Stock = Column(Float, default=0.0, nullable=False)
    Batch_KC8_Analyses = Column(String(50), nullable=True)




class DB_Batch_OGD(Base):
    __tablename__ = 'Batch_OGD'
    Batch_OGD_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Batch_OGD_name = Column(String(10), nullable=False, unique=True)
    Batch_OGD_date = Column(DateTime, nullable=False)
    Batch_OGD_Technicien = Column(String(10), nullable=False)
    Batch_OGD_KC8_batch = Column(String(10), nullable=False)
    Batch_OGD_KC8_masse = Column(Float, default=20.0, nullable=False)
    Batch_OGD_THF_batch = Column(String(50), nullable=False)
    Batch_OGD_THF_Volume = Column(Float, default=500, nullable=False)
    Batch_OGD_Temperature = Column(Float, default=20.0, nullable=False)
    Batch_OGD_Agitation = Column(Integer, nullable=False)
    Batch_OGD_heure_debut = Column(DateTime, nullable=False)
    Batch_OGD_heure_fin = Column(DateTime, nullable=True)
    Batch_OGD_room_HR = Column(Float, default=20.0, nullable=False)
    Batch_OGD_room_T = Column(Float, default=20.0, nullable=False)
    Batch_OGD_Stock = Column(Float, default=20.0, nullable=True)
    Batch_OGD_Analyses = Column(String(50), nullable=False)


class DbTechnicient(Base):
    __tablename__ = 'Techniciens'
    Technicien_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Initiales_tech = Column(String(10), nullable=False)
    Technicien_info_2 = Column(String(100), nullable=False)


class DB_Batch_Produit(Base):
    __tablename__ = 'Batch_produit'
    Batch_Produit_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Batch_Produit_ref_CW = Column(String(10), nullable=False, unique=True)
    Batch_Produit_date = Column(DateTime, nullable=False)
    Batch_Produit_Technicien = Column(String(10), nullable=False)
    Batch_Produit_OGD_batch = Column(String(10), nullable=False, unique=True)
    Batch_Produit_OGD_Qte = Column(Float, default=20.0, nullable=False)
    Batch_Produit_additif_batch = Column(String(10), nullable=False)  # can be EPO ou viscosant
    Batch_Produit_additif_Qte = Column(Float, default=20.0, nullable=False)
    Batch_produit_stock = Column(Float, default=0.0, nullable=False)
    Batch_Produit_Analyses = Column(String(50), nullable=False)


class DB_Envoi(Base):
    __tablename__ = 'Envois'
    Envoi_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Envoi_date_commande = Column(DateTime, nullable=False)
    Envoi_client_name = Column(String(50), nullable=False)
    Envoi_produit_name = Column(String(10), nullable=False)
    Envoi_produit_batch = Column(String(10), nullable=True)
    Envoi_produit_Qte = Column(Float, nullable=False)
    Envoi_produit_emballage = Column(String(10), nullable=False)
    Envoi_date_prevu = Column(DateTime, nullable=True)
    Envoi_date_effective = Column(DateTime, nullable=True)
    Envoi_code_coli = Column(String(50), nullable=True, unique=True)
    Envoi_delivered = Column(DateTime, nullable=True)
    Envoi_retour_client = Column(JSON, nullable=True)
    
class DB_Client(Base):
    __tablename__ = 'Clients'
    Client_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Client_nom = Column(String(50), nullable=False)
    Client_adresse = Column(String(50), nullable=False)

