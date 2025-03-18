import pandas as pd
import numpy as np
import joblib
import json
import requests
from datetime import datetime
#### schemas
from typing import Dict, List, Any
from pydantic import BaseModel

class Data_In(BaseModel):
    Batch_OGD_name:str
    Batch_OGD_date: datetime
    Batch_OGD_Technicien:str
    Batch_OGD_KC8_batch:str
    Batch_OGD_KC8_masse: float
    Batch_OGD_THF_batch:str
    Batch_OGD_THF_Volume: float
    Batch_OGD_Temperature: float
    Batch_OGD_Agitation:float
    Batch_OGD_heure_debut: datetime
    Batch_OGD_heure_fin: datetime
    Batch_OGD_room_HR:float
    Batch_OGD_room_T: float
    Batch_OGD_Stock: float
    Batch_OGD_Analyses:str
    
class Data_Out(BaseModel):
    pred:float

class Data_group_out(BaseModel):
    pred:float

    
#### helper function
def get_maree_data(years : list):
    """Cette fonction se connecte à une API externe pour récuperer des données si elle ne sont pas déja présentes"""
    try :
        gde_marees = joblib.load("app/data/ML_sup/gde_maree.bin")
        print("Donées grandes marées disponibles")
        return gde_marees

    except:
        print("Téléchargement données grandes marées")
        gde_marees = pd.DataFrame()
        for year in years:
            url = f"https://data.stmalo-agglomeration.fr/api/explore/v2.1/catalog/datasets/grandes-marees-a-saint-malo/records?limit=20&refine=date%3A%22{year}%22"
            gde_marees = pd.concat([gde_marees,pd.DataFrame(json.loads(requests.get(url).content)['results'])],axis=0)
        # gde_marees
        gde_marees["date"] = pd.to_datetime(gde_marees["date"])
        joblib.dump(gde_marees,"app/data/ML_sup/gde_maree.bin")
        return gde_marees
    
def check_if_within_range(row, check_times):
    """
    Compte le nombre de datetimes dans check_times qui tombent dans la plage
    définie par Heure_debut et Heure_ajout2.
    """
    return sum(row["Batch_OGD_heure_debut"] <= check_time <= row["Batch_OGD_heure_fin"] for check_time in check_times)

def clean_data(data):

    # find columns names that have unique values or identical values (not usefull for ML model)
    data.drop(index=['Batch_OGD_name', 'Batch_OGD_THF_batch', 'Batch_OGD_Stock'],inplace=True)

    # Data Engineering
    try:
        data['conc_KC8'] = data['Batch_OGD_KC8_masse'] / data['Batch_OGD_THF_Volume']
    except:
        data['conc_KC8'] = 0.04
    finally:
        data.drop(index=['Batch_OGD_KC8_masse','Batch_OGD_THF_Volume'],inplace=True)

    # Handeling time data (transform to datetime format)
    datetime_to_remove = list()
    for index in data.index:
        if 'heure' in index or 'date' in index:
            data[index] = pd.to_datetime(data[index])
            datetime_to_remove.append(index)

    print(type(data['Batch_OGD_date']))
    data['month_production'] = data['Batch_OGD_date'].month
    data['day_production_start'] = data['Batch_OGD_date'].day
    data['days_exfo'] = (data['Batch_OGD_heure_fin'] - data['Batch_OGD_heure_debut']).days

    # ajouter année au batch KC8 
    data['Batch_OGD_KC8_batch'] = str(data.Batch_OGD_date.year) + "-" + data.Batch_OGD_KC8_batch

    # Ajoute data autre source
    gde_marees = get_maree_data(years = [2022,2023,2024,2025])
    data["exfo_gde_maree"] =  check_if_within_range(data, gde_marees['date'])
    data.drop(index=datetime_to_remove, inplace=True)

    return data



