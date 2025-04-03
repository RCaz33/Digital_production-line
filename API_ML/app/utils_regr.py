
import numpy as np
import requests
import logging
import pandas as pd
import joblib
import pickle
import json
from datetime import datetime

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import ElasticNetCV, ElasticNet
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_validate
from sklearn.model_selection import ShuffleSplit

import mlflow
from mlflow.models import infer_signature

import os
from dotenv import load_dotenv
load_dotenv()


# initialisation des connections externes
url = 'http://127.0.0.1:8000'
headers = {
'accept': 'application/json',
'Content-Type': 'application/json'}


def collect_data():
    """
    Cette fonction permet de collecter les données depuis une base de données externe
    pour entraine un nouveaux modele sklearn
    """
    # gestion des exeptions / erreurs
    try:
        response = requests.get(f'{url}/OGD/', headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f" Cannot connect to database\nRequest failed: {e}")
    
    # traitement et sauvegarde pour entrainement ML 
    metadata = pd.DataFrame(response.json())
    mask = metadata.Batch_OGD_name.to_list()

    try:
        response = requests.get(f'{url}/analyses/', headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f" Cannot connect to database\nRequest failed: {e}")
    
    analyses = pd.DataFrame(response.json())
    analyses = analyses.loc[analyses['Analyse_subname']=='UV']
    out=list()
    for i in range(len(analyses)):
        target=dict()
        target['sample'] = analyses.loc[i,'Analyse_name']
        target['conc'] = analyses.loc[i,'Analyse_details']['conc']
        out.append(target)
    targets = pd.DataFrame(out)
    targets = targets.loc[targets['sample'].isin(mask)]

    all = pd.merge(metadata,targets,left_on='Batch_OGD_name',right_on='sample',how='inner')
    metadata = all.iloc[:,:-2]
    targets = all.loc[:,'conc']

    return metadata, targets

#### helper function
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
        print(os.listdir("."))
        joblib.dump(gde_marees,"app/data/ML_sup/gde_maree.bin")
        print("DONNEES GRANDES MAREES TELECHARGEES")
        return gde_marees
    
def check_if_within_range(row, check_times):
    """
    Compte le nombre de datetimes dans check_times qui tombent dans la plage
    définie par Heure_debut et Heure_ajout2.
    """
    return sum(row["Batch_OGD_heure_debut"] <= check_time <= row["Batch_OGD_heure_fin"] for check_time in check_times)

def clean_data(data):
    """ this function prepare the raw data for ML model : feature ingineering, data cleaning, data transformation"""
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



# prepare data for ML
def set_preprocessor(X):
    """this function instanciate and test a sklearn preprocessor"""
    categorical_columns = ['Batch_OGD_Technicien','Batch_OGD_KC8_batch', 'Batch_OGD_Analyses',
                        'month_production','day_production_start','exfo_gde_maree']

    numerical_columns = ['Batch_OGD_Temperature','Batch_OGD_Agitation','Batch_OGD_room_HR',
                    'conc_KC8','Batch_OGD_room_T','days_exfo']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('numerical', StandardScaler(),numerical_columns),
            ('categorical',OneHotEncoder(sparse_output=False,handle_unknown='ignore'),categorical_columns)])
    try:
        preprocessor.fit(X.iloc[:2,:])
        return preprocessor
    except:
        return ("set_preprocessor is not working, check columns names")
    
def get_best_params_elasticnet(X,y):
    """this function instanciate and test a sklearn preprocessor"""

    # cherche les meilleurs hyperparametres
    cv_model = ElasticNetCV(l1_ratio=[.1, .5, .9, .95, .995, 1], eps=0.001, n_alphas=50, fit_intercept=True, 
                            precompute=True, max_iter=10000, tol=0.0001, cv=ShuffleSplit(n_splits=10,test_size=0.2), 
                            copy_X=True, verbose=0, n_jobs=-1, positive=False, random_state=42, selection='cyclic')
    pipe = Pipeline([('preprocessor',set_preprocessor(X)),
                     ('cv_model',cv_model)])
    pipe.fit(X,y)

    # Extract the MSE path, the alphas and l1_ratios
    mse_path = pipe.named_steps["cv_model"].mse_path_
    alphas = [float(a) for a in cv_model.alphas_[0]] #cv_model.alphas_
    l1_ratios = cv_model.l1_ratio
    # Iterate over each combination of alpha and l1_ratio

    print("END hyperparameters search for ELASTICNET CV")          
    print("best l1 ratio",cv_model.l1_ratio_)
    print("best alpha",cv_model.alpha_)
    return cv_model.l1_ratio_, cv_model.alpha_

def dump_pickle(obj, filename: str):
    """Cette fonction sers à sauvegarder un fichier pickle"""
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)

def log_best_elastic_net_model(where_to_log : str, algo_type : str):

    """ search best hyperparameters for elasticnet
    uses mlflow to register experiment by date,
    can save artifact locally or on blob storage"""

    # prepare data and preprocessing
        # collect from BDD
    metadata, target = collect_data()
    X = metadata.apply(clean_data, axis=1)
    preprocessor = set_preprocessor(X)
    y=target

    # get best params for a given date
    date = datetime.now().strftime('%Y-%m-%d')

    # Cross-validation with best params
    if algo_type == 'elasticnet':
        best_l1_ratio, best_alpha = get_best_params_elasticnet(X,y)
        # cross validated score for elastic net 
        model = ElasticNet(alpha=best_alpha, l1_ratio=best_l1_ratio, fit_intercept=True, 
                    precompute=True, max_iter=10000, tol=0.0001,
                    copy_X=True, positive=True, random_state=42, selection='cyclic')
        # pipe = Pipeline([('preprocessor',set_preprocessor(X)),
        #             ('model',model)])
    
        # results = cross_validate(pipe,X,y,cv=ShuffleSplit(n_splits=15,test_size=0.2),
        #                     return_train_score=True,
        #                     scoring="neg_root_mean_squared_error")
        


    # elif algo_type == 'sgdregr':
    #     best_params = get_best_params_sgdregr(X,y,tracking_uri,date)
    #     model = SGDRegressor(**best_params)
    #     pipe = Pipeline([('preprocessor',set_preprocessor(X)),
    #                 ('model',model)])
    #     results = cross_validate(pipe,X,y,cv=ShuffleSplit(n_splits=15,test_size=0.2),
    #                         return_train_score=True,
    #                         scoring="neg_root_mean_squared_error")
        

    # configure mflflow for azure
    print("START LOGGING FINAL MODEL")
    if where_to_log == 'azure_blob':
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        subscription_id = os.getenv("SIMPLON_AZURE_SUBSCRIPTION_ID")
        resource_group = os.getenv('SIMPLON_AZURE_RESSOURCE_GROUP')
        workspace = os.getenv("SIMPLON_AZURE_WORKSPACE")

        ml_client = MLClient(credential=DefaultAzureCredential(),
                                subscription_id=subscription_id, 
                                resource_group_name=resource_group,
                                workspace_name=workspace)

        mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)

    elif where_to_log == 'local':
        mlflow.set_tracking_uri("http://127.0.0.1:8080")
        preprocessor = set_preprocessor(X)
        X_transfo = preprocessor.fit_transform(X)
        df_transfo = pd.DataFrame(X_transfo,columns=preprocessor.get_feature_names_out())
        df_transfo.columns = df_transfo.columns.astype(str)
        _=model.fit(df_transfo,y)
        dump_pickle(preprocessor, f"app/data/ML_sup/preprocessor.pkl")
        dump_pickle(model, f"app/data/ML_sup/elasticnet_model.pkl")

    
    # log model and artifact trained on the entire dataset
    with mlflow.start_run(run_name=f"{date}_{algo_type}_best_model_run") as run:
        run_id = run.info.run_id 
        print('ACTIVE RUN_ID - after start run',mlflow.active_run().info.run_id)   


        print(10*"\n")
        print("PREPROCESSOR")
        # fit the preprocessor and model
        preprocessor = set_preprocessor(X)
        print(X.shape)
        print(X.columns)
        X = preprocessor.fit_transform(X)
        print(X.shape)
        col_names = [a.replace('__','_') for a in preprocessor.get_feature_names_out()]
        X = pd.DataFrame(X,columns=col_names)
        _ = model.fit(X,y)

        # log predictions

        # first log preprocessor 
        preprocessor_name = f"{date}_preprocessor.pkl"
        joblib.dump(preprocessor, preprocessor_name)
        mlflow.log_artifact(preprocessor_name)
        os.remove(preprocessor_name)

        # log variable name and coef if coef > 0 
        params_to_log={a.replace('__','_'):b for a,b in zip(preprocessor.get_feature_names_out()[model.coef_>0],model.coef_[model.coef_>0])}
        params_to_log
        mlflow.log_param("model",algo_type)
        mlflow.log_metrics(params_to_log)

        # log model with flavor
        registered_model_name=f"best_{algo_type}_model_on_{date}"
        artifact_path="logged_model"
        mlflow.sklearn.log_model(sk_model=model,
                                     signature=infer_signature(X.iloc[:10,:],model.predict(X.iloc[:10,:])),
                                     registered_model_name=registered_model_name, # <-- registered name
                                     artifact_path =artifact_path) # if azure, make sure to set atifcact path as model:/experiemtname/model
            
        
    
    

    print("END LOGGING FINAL MODEL")
    print(100*'*')
    print(f"MODEL_URI : runs:/{run_id}/{artifact_path}")
    print(f"MODEL_NAME : best_{algo_type}_model_on_{date}")
    print(100*'*')
    print(f"PREPROCESSOR_PATH : runs:/{run_id}/{preprocessor_name}")
    print(100*'*')
    # elif log_method == "create registered model":
    #     client = MlflowClient()
    #     result = client.create_model_version(name="best_model_on_{date}",
    #                                          source="artifact/")

    return model