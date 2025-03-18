# import des librairies
import os
import pickle
import json
import joblib
import click
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
        X = X = pd.read_csv(f"{raw_data_path}/X.csv",index_col=0)
        y = pd.read_csv(f"{raw_data_path}/y.csv",index_col=0)
        y = y['QC_Conc_OGD'].astype(float)
        return X, y
    except:
        return "les données n'existent pas, essayez de les générer / nettoyer en premier ou changez de dossier"

# prepare data for ML
def set_preprocessor(X):
    """this function instanciate and test a sklearn preprocessor"""
    categorical_columns = ['Technicien_id', 'Batch_KC8', 'Ref_plaque', 
       'Technicien_id.1',  'Centrifugation', 'Technicien_id.2', 'Lab_HR.2',
       'Lab_T.2', 'Technicien_id.3','month_production',  ]

    numerical_columns = ['Vitesse_agitation',
        'Lab_HR', 'Lab_T', 'BaG_T', 'BaG_H2O_ppm', 'BaG_O2_ppm','Lab_HR.1', 'Lab_T.1', 'BaG_T.1', 'BaG_H2O_ppm.1',
        'BaG_O2_ppm.1', 'conc_KC8', 'volume_O2','days_exfo', 'sediment_time','exfo_gde_maree']

    preprocessor = ColumnTransformer(
        transformers=[
            ('numerical', StandardScaler(),numerical_columns),
            ('categorical',OneHotEncoder(sparse_output=False,handle_unknown='ignore'),categorical_columns)])
    try:
        preprocessor.fit(X)
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
    mlflow.set_experiment(f"/{date}Carbon_waters_Saving_pipeline_linear_model")

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
            
            cv = cross_validate(pipeline,X,y,cv=ShuffleSplit(n_splits=5,test_size=test_size),return_train_score=True)
            
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
