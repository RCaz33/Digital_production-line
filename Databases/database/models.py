from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Boolean, DateTime, Float, Time
from database.db_connect import Base
from sqlalchemy import Column, JSON




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
    Batch_Produit_stabilisant_bacth = Column(String(10), nullable=False)  # can be EPO ou viscosant
    Batch_Produit_stabilisant_Qte = Column(Float, default=20.0, nullable=False)
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
    Envoi_date_prevu = Column(DateTime, nullable=False)
    Envoi_date_effective = Column(DateTime, nullable=True)
    Envoi_code_coli = Column(String(50), nullable=True, unique=True)
    Envoi_delivered = Column(Boolean)
    Envoi_retour_client = Column(JSON, nullable=True)
    
class DB_Client(Base):
    __tablename__ = 'Clients'
    Client_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Client_nom = Column(String(50), nullable=False)
    Client_adresse = Column(String(50), nullable=False)

# class DbForm_S0(Base):
#     __tablename__ = 'Batch_OGD'
#     # exacly the column name in the database to allow orm queries
#     Batch_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     Batch_name = Column(String(10), nullable=False)
#     Batch_THF_ref = Column(String(10), nullable=False)

    # If there are any relationships, they can be defined here
    # For example:
    # user_id = Column(Integer, ForeignKey('users.id'))
    # user = relationship('DbUser', back_populates='forms')


# class DbForm_S1(Base):
#     __tablename__ = 'Etape1_lancement'

#     Batch_id = Column(Integer, primary_key=True, index=True)
#     Date = Column(DateTime, nullable=False)
#     Technicien_id = Column(Integer, nullable=False)
#     Batch_KC8 = Column(String(20), nullable=False)
#     Masse_KC8 = Column(Float, default=20.0, nullable=False)
#     Volume_THF = Column(Integer, default=500, nullable=False)
#     Ref_plaque = Column(Integer, nullable=False)
#     Vitesse_agitation = Column(Integer, default=230, nullable=False)
#     Heure_debut = Column(DateTime, nullable=False)
#     Lab_HR = Column(Float, default=0.0, nullable=False)
#     Lab_T = Column(Float, default=0.0, nullable=False)
#     BaG_T = Column(Float, default=0.0, nullable=False)
#     BaG_H2O_ppm = Column(Float, default=0.0, nullable=False)
#     BaG_O2_ppm = Column(Float, default=0.0, nullable=False)
#     Observations = Column(String(255), nullable=True)

# class DbForm_S2(Base):
#     __tablename__ = 'Etape2_THF_Sedim_Centri'

#     Batch_id = Column(Integer, primary_key=True, index=True)
#     Date = Column(DateTime, nullable=False)
#     Technicien_id = Column(String(5), nullable=False)
#     Ajout_THF_JourJ = Column(Boolean, default=False, nullable=False)
#     Heure_ajout2 = Column(Time, nullable=False)
#     Volume_THF_ajout2 = Column(Integer, default=500, nullable=False)
#     Heure_debut_sedimentation = Column(Time, nullable=False)
#     Heure_fin_sedimentation = Column(String(255), nullable=True)
#     Sediments = Column(String(255), nullable=True)
#     Ctrl_visuel_couleur = Column(String(255), nullable=True)
#     Lab_HR = Column(Float, default=0.0, nullable=False)
#     Lab_T = Column(Float, default=0.0, nullable=False)
#     BaG_T = Column(Float, default=0.0, nullable=False)
#     BaG_H2O_ppm = Column(Float, default=0.0, nullable=False)
#     BaG_O2_ppm = Column(Float, default=0.0, nullable=False)
#     Observations = Column(String(255), nullable=True)
#     Centrifugation = Column(Boolean, nullable=False)

# class DbForm_S3(Base):
#     __tablename__ = 'Etape3_Oxydation'

#     Batch_id = Column(Integer, primary_key=True, index=True)
#     Date = Column(DateTime, nullable=False)
#     Technicien_id = Column(String(5), nullable=False)
#     Debit_air_synthetique = Column(Float, default=0.0, nullable=False)
#     Temps_oxidation = Column(Float, default=30.0, nullable=False)
#     Lab_HR = Column(Float, nullable=False)
#     Lab_T = Column(Float, nullable=False)
#     Observations = Column(String(255), nullable=True)


# class DbForm_S4(Base):
#     __tablename__ = 'Etape4_CtrlQualite'

#     Batch_id = Column(Integer, primary_key=True, index=True)
#     Date = Column(DateTime, nullable=False)
#     Technicien_id = Column(String(5), nullable=False)
#     m_OGD = Column(Float, default=0.0, nullable=False)
#     m_THF = Column(Float, default=0.0, nullable=False)
#     Abs_800 = Column(Float, default=0.0, nullable=False)
#     QC_Conc_OGD = Column(Float, nullable=False)
#     QC_Categorie = Column(Integer, nullable=False)
#     Stockage_recipient = Column(String(255), default='na', nullable=False)
#     Stockage_Emplacement = Column(String(255), default='na', nullable=False)
#     Stockage_Utilisation = Column(String(255), default='na', nullable=False)
#     Observations = Column(String(255), nullable=True)


# class DbForm_KC8(Base):
#     __tablename__ = 'Batch_KC8'

#     KC8_id = Column(Integer, primary_key=True, index=True)
#     KC8_Date = Column(DateTime, nullable=False)
#     KC8_Initiales = Column(String(5), nullable=False)
#     Batch_KC8_name = Column(String(10), nullable=False)
#     KC8_Lab_HR = Column(Float, nullable=False)
#     KC8_Lab_T = Column(Float, nullable=False)
#     KC8_BaG_T = Column(Float, nullable=False)
#     KC8_BaG_O2_ppm = Column(Float, default=0.0, nullable=False)
#     KC8_Bag_H20_ppm = Column(Float, nullable=False)
#     KC8_Batch_Graphite = Column(String(255), default='A1.', nullable=False)
#     KC8_Batch_K = Column(String(255), default='10224825', nullable=False)
#     KC8_masse_K = Column(Float, default=4.0, nullable=False)
#     KC8_masse_C = Column(Float, default=10.0, nullable=False)
#     KC8_Heating_thermostat_ref = Column(String(255), default='3', nullable=False)
#     KC8_Heating_Start_Heure = Column(Time, nullable=False)
#     KC8_Heating_End_Heure = Column(Time, nullable=False)
#     KC8_Visual_verification = Column(Boolean, nullable=False)
#     KC8_Observation = Column(String(255), default='na', nullable=False)
#     KC8_Analsysis_date = Column(DateTime, nullable=False)
#     KC8_Analysis_Initiales = Column(String(5), nullable=False)
#     KC8_Analysis_validation = Column(Boolean, nullable=False)
#     KC8_Analysis_Observation = Column(String(255), default='na', nullable=False)