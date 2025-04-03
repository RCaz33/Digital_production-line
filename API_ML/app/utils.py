import pandas as pd
import numpy as np
import joblib
import json
import requests
from datetime import datetime
import pickle
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
def load_pickle(filename:str):
    with open(filename, 'rb') as file:
        return pickle.load(file)
    
def get_maree_data(years : list):
    """Cette fonction se connecte à une API externe pour récuperer des données si elle ne sont pas déja présentes"""
    try :
        gde_marees = joblib.load("app/data/ML_sup/gde_maree.bin")
        return gde_marees

    except:
        gde_marees = pd.DataFrame()
        for year in years:
            url = f"https://data.stmalo-agglomeration.fr/api/explore/v2.1/catalog/datasets/grandes-marees-a-saint-malo/records?limit=20&refine=date%3A%22{year}%22"
            gde_marees = pd.concat([gde_marees,pd.DataFrame(json.loads(requests.get(url).content)['results'])],axis=0)

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





import sklearn
import io
import base64
import os

def make_chart_for_dash_produits(last_n = 5):

    # because mac OS, need to set backend to agg
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    print(os.listdir("."))
    # get values to be updated
    sc_UV = joblib.load("app/data/sc_UV.joblib")
    indicator_UV=joblib.load("app/data/indicator_UV.joblib")
    pca_UV=joblib.load("app/data/pca_UV.joblib")
    weights_UV=joblib.load("app/data/weights_UV.joblib")
    kmeans_UV=joblib.load("app/data/kmeans_UV.joblib")

    sc_RAMAN=joblib.load("app/data/sc_RAMAN.joblib")
    indicator_RAMAN=joblib.load("app/data/indicator_RAMAN.joblib")
    pca_RAMAN=joblib.load("app/data/pca_RAMAN.joblib")
    weights_RAMAN=joblib.load("app/data/weights_RAMAN.joblib")
    kmeans_RAMAN=joblib.load("app/data/kmeans_RAMAN.joblib")

    # make the API CALL (take sample with analytic data)
    response = requests.get('http://127.0.0.1:8000/analyses/')
    analyzed_names = [a['Analyse_name'] for a in response.json()]
    response = requests.get('http://127.0.0.1:8000/OGD/')
    OGD_all = pd.DataFrame(response.json())
    OGD_all = OGD_all.loc[OGD_all['Batch_OGD_name'].isin(analyzed_names)]
    last_5 = OGD_all['Batch_OGD_name'][-last_n:].values

    # fetch analysis
    UV_data=pd.DataFrame()
    RAMAN_data=pd.DataFrame()
    print(5*"\n")
    for OGD_n in last_5:
        print(OGD_n)
        try:
            response = requests.get(f'http://127.0.0.1:8000/analyses/name/{OGD_n}')
            analyses = pd.DataFrame(response.json())
            analyse_UV = analyses.loc[analyses.Analyse_subname == 'UV']
            analyse_RAMAN = analyses.loc[analyses.Analyse_subname == 'RAMAN']
            UV_data = pd.concat([UV_data,analyse_UV])
            RAMAN_data = pd.concat([RAMAN_data,analyse_RAMAN])
        except Exception as e:
            print("EEERROR",e)
            last_5 = last_5[~np.isin(last_5,[OGD_n])]
            last_n -= 1


    print(19*"\n")
    print(UV_data['Analyse_details'])
    # prepare UV with dillution
    UV_spectra = pd.DataFrame(UV_data['Analyses_data'].tolist()).astype(float)
    dillution_factor = pd.Series(UV_data['Analyse_details'].apply(lambda x : int(x['dilution'].split(":")[1])  if 'dilution' in x.keys() else 10),name='dillution_factor')
    UV_spectra_dill = UV_spectra.mul(dillution_factor.reset_index(drop=True),axis=0)

    

    print(5*"\nUVSPECTRA")


    print((UV_data['Analyses_data'][0]))

    
    # generate indicators
    indic_UV = (UV_spectra_dill.loc['200',:] / UV_spectra_dill.loc['490',:])[-last_n:]
    indic_UV.index=last_5
    indic_RAMAN = RAMAN_data['Analyse_details'].apply(lambda x : x['group1_indic1-ex D/G'])[-last_n:]
    indic_RAMAN.index=last_5

    # prepare sample with scaling and PCA transform
    sample_UV = pca_UV.transform(sc_UV.transform(UV_spectra_dill))
    sample_RAMAN = pca_RAMAN.transform(sc_RAMAN.transform(pd.DataFrame(RAMAN_data['Analyses_data'].tolist()).astype(float)))


# make figure
    f_UV, ax = plt.subplots(1,2,figsize=(6,3))
    ax[0].scatter(weights_UV[:,0],weights_UV[:,1], c=kmeans_UV.labels_)
    ax[0].scatter(sample_UV[:,0],sample_UV[:,1],c='red')
    ax[1].boxplot(x=indicator_UV,showfliers=False)
    ax[1].scatter([1 for i in range(last_n)],indic_UV,c='red')
    for label in indic_UV.index:
        ax[1].text(1.1,indic_UV[label],s=label)
    plt.suptitle('Analyse UV')
    img = io.BytesIO()
    plt.savefig(img,format='png')
    img.seek(0)
    img_UV = base64.b64encode(img.getvalue()).decode('utf-8')

    f_RAMAN, ax = plt.subplots(1,2,figsize=(6,3))
    ax[0].scatter(weights_RAMAN[:,0],weights_RAMAN[:,1], c=kmeans_RAMAN.labels_)
    ax[0].scatter(sample_RAMAN[:,0],sample_RAMAN[:,1], c='red')
    ax[1].boxplot(x=indicator_RAMAN)
    ax[1].scatter([1 for i in range(last_n)],indic_RAMAN,c='red')
    for label in indic_RAMAN.index:
        ax[1].text(1.01,indic_RAMAN[label],s=label)
    plt.suptitle('Analyse RAMAN')

    img = io.BytesIO()
    plt.savefig(img,format='png')
    img.seek(0)
    img_RAMAN = base64.b64encode(img.getvalue()).decode('utf-8')

    return img_UV, img_RAMAN