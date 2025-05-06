# import des librairies
import os
import pickle
import json
import joblib
import click
import numpy as np
import pandas as pd
import requests



from datetime import datetime

import mlflow
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression,ElasticNet,SGDRegressor
from sklearn.ensemble import RandomForestRegressor
from itertools import product
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_validate, ShuffleSplit


######### ENVIRON VARIABLE
# export MLFLOW_ARTIFACT_URI="file:/path" 


# test if tracking server
def test_tracking_server_connection_ok(tracking_uri):
    print("IS TESTING TRACKING URI ...")
    try:
        response = requests.get(f"{tracking_uri}/health", timeout=2)
        if response.status_code == 200:
            return "connection à MLFlow ok"
        else:
            return f"Failed to connect: Status code {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Connection to MLFlow server impossible: {e}"

# load data
def load_data(raw_data_path):
    """ this function tries to load data if it exist"""
    try:
        X = X = pd.read_csv(f"{raw_data_path}/new_data.csv",index_col=0) # new data is the one sent to new db
        y = pd.read_csv(f"{raw_data_path}/y.csv",index_col=0)
        y = y['QC_Conc_XY'].astype(float)
        return X, y
    except:
        return "les données n'existent pas, essayez de les générer / nettoyer en premier ou changez de dossier"

def get_maree_data(years : list):
    """Cette fonction se connecte à une API externe pour récuperer des données si elle ne sont pas déja présentes"""
    try :
        gde_marees = joblib.load("data/gde_maree.bin")
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
        joblib.dump(gde_marees,"data/gde_maree.bin")
        return gde_marees
    
def check_if_within_range(row, check_times):
    """
    Compte le nombre de datetimes dans check_times qui tombent dans la plage
    définie par Heure_debut et Heure_ajout2.
    """
    return sum(row["Batch_XY_heure_debut"] <= check_time <= row["Batch_XY_heure_fin"] for check_time in check_times)

def clean_data(data):

    # Handeling duplicates
    duplicates = data.duplicated(subset=['Batch_XY_name','Batch_XY_date'])
    data = data.loc[~duplicates]

    # Handeling null values
    null_values = list()
    for col in data.columns:
        if data[col].isnull().sum() > data.shape[0]/3:
            null_values.append(col)
    data.drop(columns=null_values,inplace=True)

    # Handeling unique values
    variable_to_remove = list()
    count_unique = data.astype(str).describe().T

    # find columns names that have unique values or identical values (not usefull for ML model)
    for i in range(count_unique.shape[0]):
        if count_unique.iloc[i,1] == 280 or count_unique.iloc[i,1] == 1:
            variable_to_remove.append(data.columns[i])
    data[variable_to_remove].astype(str).describe()
    data.drop(columns=variable_to_remove,inplace=True)


    # Data Engineering
    data['conc_XX'] = data['Batch_XY_XX_masse'] / data['Batch_XY_YY_Volume']
    data.drop(columns=['Batch_XY_XX_masse','Batch_XY_YY_Volume'],inplace=True)


    # Handeling time data (transform to datetime format)
    datetime_to_remove = list()
    for col in data.columns:
        if 'heure' in col or 'date' in col:
            data[col] = pd.to_datetime(data[col])
            datetime_to_remove.append(col)

    data['month_production'] = data['Batch_XY_date'].dt.month
    data['day_production_start'] = data['Batch_XY_date'].dt.day
    data['days_exfo'] = (data['Batch_XY_heure_fin'] - data['Batch_XY_heure_debut']).dt.days

    # ajouter année au batch XX 
    data.loc[:,'Batch_XY_XX_batch'] = data.Batch_XY_date.dt.year.astype(str) + "-" + data.Batch_XY_XX_batch

    # Ajoute data autre source
    gde_marees = get_maree_data(years = [2022,2023,2024,2025])
    data["exfo_gde_maree"] =  data.apply(lambda row: check_if_within_range(row, gde_marees['date']), axis=1)
    data.drop(columns=datetime_to_remove, inplace=True)

    # impute valeur absurdes
    for var in ['Batch_XY_Temperature','Batch_XY_room_HR','Batch_XY_room_T','conc_XX','days_exfo','exfo_gde_maree']:
        _ = data.loc[data[var] != 0, ["month_production",var]]
        _dict = _.groupby(['month_production'])[var].mean().to_dict()

        if not var in ['days_exfo','exfo_gde_maree']:
            data.loc[data[var] == 0, var] = data.loc[data[var] == 0, 'month_production'].map(_dict)
        else:
            Q1 = np.percentile(data[var], 25)
            Q3 = np.percentile(data[var], 75)
            IQR = Q3 - Q1
            # Définir les seuils pour les outliers
            low_fly = Q1 - 1.5 * IQR
            up_fly = Q3 + 1.5 * IQR
            data.loc[(data[var] < low_fly) | (data[var]> up_fly),var] = data.loc[(data[var] < low_fly) | (data[var]> up_fly), 'month_production'].map(_dict)

    return data

# prepare data for ML
def set_preprocessor(X):
    """this function instanciate and test a sklearn preprocessor"""
    categorical_columns = ['Batch_XY_Technicien','Batch_XY_XX_batch', 'Batch_XY_Analyses',
                        'month_production','day_production_start','exfo_gde_maree']


    numerical_columns = ['Batch_XY_Temperature','Batch_XY_Agitation','Batch_XY_room_HR',
                    'conc_XX','Batch_XY_room_T','days_exfo']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('numerical', StandardScaler(),numerical_columns),
            ('categorical',OneHotEncoder(sparse_output=False,handle_unknown='ignore'),categorical_columns)])
    try:
        # preprocessor.fit(X)
        return preprocessor
    except:
        return ("set_preprocessor is not working, check columns names")


# script de préparation des données
@click.command()
@click.option(
    "--tracking_uri", default='http://127.0.0.1:8080', prompt='Tracking uri',
    help="Serveur ou les données mlflow sont stockées"
)
@click.option(
    "--raw_data_path", default='data', prompt='Raw data path',
    help="Dossier ou les données brutes (X,y) sont stockées"
)


def test_5_models(tracking_uri : str, raw_data_path : str):

    """ uses mlflow to register experiment by date,
    can save artifact locally or on blob storage"""

    # test connection to tracking server
    _ = test_tracking_server_connection_ok(tracking_uri)

    # prepare data and preprocessing
    X, y = load_data(raw_data_path)
    X = clean_data(X)
    X.to_csv("data/new_X.csv")
    preprocessor = set_preprocessor(X)

    # prepare search parameters
    test_sizes = [0.1,0.2,0.3,0.4,0.5]
    dummy = DummyRegressor()
    linear = LinearRegression()
    elastic = ElasticNet(alpha=0.1, l1_ratio=0.8, max_iter=5000)
    sgd = SGDRegressor(max_iter=10000, tol=1e-3, loss='epsilon_insensitive',penalty='elasticnet')
    forest = RandomForestRegressor(max_depth=10,max_features='log2',min_samples_split=20)
    models = [dummy, linear,elastic,sgd,forest]

    # configure mlflow
    mlflow.set_tracking_uri(tracking_uri)
    date = datetime.now().strftime('%Y-%m-%d')
    mlflow.set_experiment(f"/search_algo_{date}")

    print("BEFORE RUN")
    print(mlflow.get_tracking_uri())
    print(mlflow.get_artifact_uri())

    all_results = pd.DataFrame()
    # run experiment
    for experiment_set in product(test_sizes,models):
        with mlflow.start_run(nested=True):

            # perfom tests
            test_size, model = experiment_set
            pipeline = Pipeline([('preprocessor',preprocessor),
                                    ('regressor', model)])
            
            cv = cross_validate(pipeline,X,y,cv=ShuffleSplit(n_splits=5,test_size=test_size,random_state=42),return_train_score=True)
            
            # save result in dataframe
            results = pd.DataFrame(cv)
            if results['test_score'].mean() <= 0:
                results['test_score'] = 0
            all_results = pd.concat([all_results,results.T.mean(axis=1)],axis=1)

            # log data in mlflow
            mlflow.log_params({"model":model,
                    "test_size":test_size})
            mlflow.log_metrics({'score_train_mean':results['train_score'].mean(),
                                'score_train_std':results['train_score'].std(),
                                'score_test_mean':results['test_score'].mean(),
                                'score_test_std':results['test_score'].std()})

    print("RESULTS:\n")
    all_results.columns = [a for a in product(test_sizes,models)]
    print(all_results.T.sort_values(by=['test_score','train_score'], ascending=[False,False]))
    # display best models
    # best_5_models = results.sort_values(by=['score_test_mean','score_test_std','score_train_mean','score_train_std'],
    #                     ascending=[False,True,False,True]).iloc[:5,:].values
    # print(best_5_models)    


if __name__ == '__main__':
    test_5_models()
