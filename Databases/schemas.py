from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime



## MUST HAVE THE SAME NAME AS IN MODELS.PY 


class Analyses_UV_Base(BaseModel):
    Analyses_UV_id = int
    Analyse_UV_name = str
    Analyse_UV_subname = str
    Analyse_UV_details = str
    Analyses_UV_data = Dict[str:Any]


class Analyses_UV_Add(BaseModel):
    Analyse_UV_name = str
    Analyse_UV_subname = str
    Analyse_UV_details = str
    Analyses_UV_data = Dict[str:Any]


class Analyses_Base(BaseModel):
    Analyses_id : int 
    Analyse_path_to_raw : str
    Analyse_code : str # 'CodeEchantillon_date_type_details'
# every folder create create a new analyse
#  
class Analyses_Base_Add(BaseModel):
    Analyse_path_to_raw : str
    Analyse_code : str # 'CodeEchantillon_date_type_details'
# every folder create create a new analyse
#  
# name of batch + date of analysis + type of analysis + details analysis
                      # "nom_250129_Raman / nom_250202_DLS / .."
class Matieres_premieres_Base(BaseModel):
    MP_id : int 
    MP_nom : str 
    MP_codeCW : str
    MP_ref_fournisseur : str 
    MP_date_reception : datetime
    MP_quantite : float
    MP_unite : str
    MP_Analyses : str 

class Matieres_premieres_Add(BaseModel):
    MP_nom : str 
    MP_codeCW : str
    MP_ref_fournisseur : str 
    MP_date_reception : datetime
    MP_quantite : float
    MP_unite : str
    MP_Analyses : str # name of batch + date of analysis + type of analysis + details analysis
   
class Batch_KC8_Base(BaseModel):
    Batch_KC8_id : int 
    Batch_KC8_name : str
    Batch_KC8_date : datetime
    Batch_KC8_Technicien : str
    Batch_KC8_K_batch : str
    Batch_KC8_C_batch : str 
    Batch_KC8_masse : int
    Batch_KC8_Temperature : float
    Batch_KC8_Agitation : int 
    Batch_KC8_heure_debut : datetime
    Batch_KC8_heure_fin : Optional[datetime] = None  
    Batch_KC8_room_HR : float
    Batch_KC8_room_T : float
    Batch_KC8_Analyses : str 

class Batch_KC8_Add(BaseModel):
    Batch_KC8_name : str
    Batch_KC8_date : datetime
    Batch_KC8_Technicien : str
    Batch_KC8_K_batch : str
    Batch_KC8_C_batch : str 
    Batch_KC8_masse : int
    Batch_KC8_Temperature : float
    Batch_KC8_Agitation : int 
    Batch_KC8_heure_debut : datetime
    Batch_KC8_heure_fin : Optional[datetime] = None  
    Batch_KC8_room_HR : float
    Batch_KC8_room_T : float
    Batch_KC8_Analyses : str 

class Batch_OGD_Base(BaseModel):
    Batch_OGD_id : int 
    Batch_OGD_name : str
    Batch_OGD_date : datetime
    Batch_OGD_Technicien : str
    Batch_OGD_KC8_batch : str
    Batch_OGD_KC8_masse : float
    Batch_OGD_THF_batch : str
    Batch_OGD_Temperature : float
    Batch_OGD_Agitation : int 
    Batch_OGD_heure_debut : datetime
    Batch_OGD_heure_fin : Optional[datetime] = None  
    Batch_OGD_room_HR : float
    Batch_OGD_room_T : float
    Batch_OGD_Analyses : str 


class Batch_OGD_Add(BaseModel):
    Batch_OGD_name : str
    Batch_OGD_date : datetime
    Batch_OGD_Technicien : str
    Batch_OGD_KC8_batch : str
    Batch_OGD_KC8_masse : float
    Batch_OGD_THF_batch : str
    Batch_OGD_Temperature : float
    Batch_OGD_Agitation : int 
    Batch_OGD_heure_debut : datetime
    Batch_OGD_heure_fin : Optional[datetime] = None  
    Batch_OGD_room_HR : float
    Batch_OGD_room_T : float
    Batch_OGD_Analyses : str 
##### Batch_OGD

# Batch data retrieved from formulaire
class Batch_OGDstep0_Base(BaseModel):
    # REQUEST DATA FROM DbFrom_S0 in models.py
    # Batch_id : int
    Step0_BatchName : str
    Step0_BatchTHF : str

# Batch data to display
class Batch_OGDstep0_Display(BaseModel):  
    # GET DATA FROM DbFrom_S0 in models.py
    Batch_id : int
    Batch_name : str
    Batch_THF_ref : str

##### TECHNICIENS

class Technicien_Create_record(BaseModel):
    Tech_name : str

# Batch data retrieved from formulaire
class Technicien_Base(BaseModel):
    # REQUEST DATA FROM DbFrom_S0 in models.py
    # Tech_id : int
    Tech_ini : str
    Tech_name : str

# Batch data to display
class Technicien_Display(BaseModel):  
    # GET DATA FROM DbFrom_S0 in models.py
    Technicien_id : int
    Initiales_tech : str
    Technicien_info_2 : str



# Batch data retrieved from formulaire
class Batch_OGDstep1_Base(BaseModel):

    Step1_BatchName : str
    Step1_Date : datetime
    Step1_Initiales : str

    Step1_KC8_Batch : str
    Step1_KC8_Masse : float
    Step1_KC8_VTHF : int

    Step1_Exfoliation_RefPlaque : int
    Step1_Exfoliation_Vitesse : int
    Step1_Exfoliation_Heure : datetime

    Step1_env_Lab_H2O : float
    Step1_env_Lab_T : float
    Step1_env_GloveBox_T : float
    Step1_env_GloveBox_H2O : float
    Step1_env_GloveBox_O2 : float

    Step1_Observation : str


# Batch data for the display
### gets data from bdd --> must have same name/type as in bdd (models.py)
class Batch_OGDStep1_Display(BaseModel):
#   items: List[Article] = []
#   model_config = ConfigDict(from_attributes = True)

    Batch_id : int
    Date : datetime
    Technicien_id : int
    Batch_KC8 : str
    Masse_KC8 : float
    Volume_THF : int
    Ref_plaque : int
    Vitesse_agitation : int
    Heure_debut: datetime
    Lab_HR : float
    Lab_T : float
    BaG_H2O_ppm : float
    BaG_O2_ppm : float
    Observations : str


class Batch_OGDstep2_Base(BaseModel):
#   items: List[Article] = []
#   model_config = ConfigDict(from_attributes = True)

    Step2_BatchName : int
    Step2_Date : datetime
    Step2_Initiales : int
    
    Step2_Ajout_THF_JourJ : bool
    Step2_Heure_ajout2 : datetime
    Step2_Volume_THF_ajout2 : float
    Step2_Heure_debut_sedimentation : datetime
    Step2_Heure_fin_sedimentation : datetime
    Step2_Sediments : str
    Step2_Ctrl_visuel_couleur : str

    Step2_env_Lab_H2O : float
    Step2_env_Lab_T : float
    Step2_env_GloveBox_T : float
    Step2_env_GloveBox_H2O : float
    Step2_env_GloveBox_O2 : float

    Step2_Observation : str
    Step2_Centrifugation : bool

class Batch_OGDStep2_Display(BaseModel):
#   items: List[Article] = []
#   model_config = ConfigDict(from_attributes = True)

    Batch_id : int
    Date : datetime
    Technicien_id : int
    Ajout_THF_JourJ : bool
    Heure_ajout2 : datetime
    Volume_THF_ajout2 : float
    Heure_debut_sedimentation : datetime
    Heure_fin_sedimentation : datetime
    Sediments : str
    Ctrl_visuel_couleur : str
    Lab_HR : float
    Lab_T : float
    BaG_T : float
    BaG_H2O_ppm : float
    BaG_O2_ppm : float
    Observations : str
    Centrifugation : bool






### gets data from bdd --> must have same name/type as in bdd (models.py)
class Batch_OGDStep3_Base(BaseModel):
#   items: List[Article] = []
#   model_config = ConfigDict(from_attributes = True)

    Step3_BatchName : int
    Step3_Date : datetime
    Step3_Initiales : int 

    Step3_Debit_air_synthetique : float
    Step3_Temps_oxidation : float

    Step3_env_Lab_H2O : float
    Step3_env_Lab_T : float
    Step3_Observations : str



### gets data from bdd --> must have same name/type as in bdd (models.py)
class Batch_OGDStep3_Display(BaseModel):
#   items: List[Article] = []
#   model_config = ConfigDict(from_attributes = True)

    Batch_id : int
    Date : datetime
    Technicien_id : int
    Debit_air_synthetique : float
    Temps_oxidation : float
    Lab_HR : float
    Lab_T : float
    Observations : str




### gets data from bdd --> must have same name/type as in bdd (models.py)
class Batch_OGDStep4_Base(BaseModel):
#   items: List[Article] = []
#   model_config = ConfigDict(from_attributes = True)

    Step4_BatchName : int
    Step4_Date : datetime
    Step4_Initiales : int

    Step4_m_OGD : float
    Step4_m_THF : float
    Step4_Abs_800 : float
    Step4_QC_Conc_OGD : float
    Step4_QC_Categorie : int

    Step4_Stockage_recipient : str
    Step4_Stockage_Emplacement : str
    Step4_Stockage_Utilisation : str
    Step4_Observations : str


### gets data from bdd --> must have same name/type as in bdd (models.py)
class Batch_OGDStep4_Display(BaseModel):
#   items: List[Article] = []
#   model_config = ConfigDict(from_attributes = True)

    Batch_id : int
    Date : datetime
    Technicien_id : int
    m_OGD : float
    m_THF : float
    Abs_800 : float
    QC_Conc_OGD : float
    QC_Categorie : int
    Stockage_recipient : str
    Stockage_Emplacement : str
    Stockage_Utilisation : str
    Observations : str
