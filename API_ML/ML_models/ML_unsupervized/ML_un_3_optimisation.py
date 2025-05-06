import os
import pickle
import click
import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
import random
import mlflow
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import hdbscan
from sklearn.metrics import silhouette_score
from datetime import datetime
from itertools import product

from dotenv import load_dotenv

load_dotenv()

def dump_pickle(obj, filename: str):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)

def load_pickle(filename:str):
    with open(filename, 'rb') as file:
        return pickle.load(file)



@click.command()
@click.option(
    "--data_path",default='2025-03-04', prompt='Location of the raw data',
    help="Location where the raw data was saved"
)
@click.option(
    "--search_new_split",  default=False, prompt='take original data and split'
)
@click.option(
    "--mode",  default='pca', prompt='Mode of spectral reduction', help="Mode of spectral reduction"
)
@click.option(
    "--train_val_split",  default=0.8, prompt='Split train/val', help="for hyperoptimisation"
)
@click.option(
    "--where_to_log",  default='specific_db', prompt='Where to store MLFlow log & artifacts'
)



def run_optimisation(data_path:str, where_to_log:str, train_val_split:int, mode:str, search_new_split:bool):

    # choose source of logs
    if where_to_log == 'local':
        mlflow.set_tracking_uri('file:///data')   
        ##########################
        # CAN SAVE INSIDE DOCKER #
        # docker run -v /host/path/to/artifacts:/container/path/to/artifacts your_mlflow_image
        # container_artifact_path = "file:///container/path/to/artifacts"
        # mlflow.set_tracking_uri(container_artifact_path)
        ##########################

    elif where_to_log == 'local_db':
        print("LOCAL_DB")
        mlflow.set_tracking_uri('sqlite:///ML_Flow_db.db')

    elif where_to_log == 'specific_db':
        print("SPECIFIC_DB")
        user = os.getenv('LOCAL_DB_USER')
        password = os.getenv('LOCAL_DB_PASS')
        db = os.getenv('LOCAL_DB_MLFLOW')
        mlflow.set_tracking_uri(f'mysql+pymysql://{user}:{password}@localhost/{db}')

    elif where_to_log == 'remote':
        print("REMOTE")
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        subscription_id = os.getenv("SIMPLON_SUBSCRIPTION_ID")
        resource_group = os.getenv('SIMPLON_RESSOURCE_GROUP')
        workspace = os.getenv("SIMPLON_WORKSPACE")

        ml_client = MLClient(credential=DefaultAzureCredential(),
                                subscription_id=subscription_id, 
                                resource_group_name=resource_group,
                                workspace_name=workspace)

        mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)

    if search_new_split:
        #load data
        meta = load_pickle(f'data/{data_path}/XY_metadata.pkl')
        raman = load_pickle(f'data/{data_path}/Analyse_raman.pkl')
        uv = load_pickle(f'data/{data_path}/Analyse_uv.pkl')

        # prepare data
        from ML_un_2_preprocess_data import preprocess, preprocess_spectral
        from sklearn.preprocessing import StandardScaler, OneHotEncoder
        # instanciate
        sc = StandardScaler()
        ohe = OneHotEncoder(sparse_output=False,handle_unknown='ignore')
        # split dataset    
        idxs = meta.Batch_XY_name.copy().tolist()
        random.shuffle(idxs)
        split=train_val_split
        idx_train = idxs[round(len(idxs)*split):]
        idx_val = idxs[:round(len(idxs)*split)]   
        # preprocess data
        meta_train, sc_fit, ohe_fit = preprocess(meta.loc[meta['Batch_XY_name'].isin(idx_train)].sort_values('Batch_XY_name'),
                                            sc,ohe,fit_dv=True)
        meta_val, sc_fit, ohe_fit = preprocess(meta.loc[meta['Batch_XY_name'].isin(idx_val)].sort_values('Batch_XY_name'),
                                            sc_fit,ohe_fit,fit_dv=False)
        out_train, out_val, reduce_r, reduce_uv = preprocess_spectral(idx_train,idx_val, raman, uv, mode=mode)
        # combine data
        data_final_train = pd.merge(meta_train, out_train, left_index=True, right_index=True)
        data_final_train.columns = data_final_train.columns.astype(str)
        data_final_val = pd.merge(meta_val, out_val, left_index=True, right_index=True)
        data_final_val.columns = data_final_val.columns.astype(str)
    else :
        data_final_train = load_pickle(f'data/{data_path}/ML_ready/train.pkl')
        data_final_val = load_pickle(f'data/{data_path}/ML_ready/val.pkl')
        data_final_train.columns = data_final_train.columns.astype(str)
        data_final_val.columns = data_final_val.columns.astype(str)


    # Log data
    # set experiment
    date = datetime.now().strftime('%Y-%m-%d')
    print(date)
    experiment_name = f"hdbscan_{date}"
    mlflow.set_experiment(experiment_name)
    mlflow.autolog()

    # Define the parameter grid
    param_grid = {
        'min_cluster_size': [5, 10, 15],
        'min_samples': [1, 2],
        'cluster_selection_epsilon': [0.0, 0.1, 0.2],
        'alpha': [1.0, 1.2, 1.4],
        'metric': ['euclidean', 'manhattan']
    }

    # Initialize variables to store the best parameters and score
    best_params = None
    best_score = -1

    # Start an MLflow run
    with mlflow.start_run():
        # Iterate over the parameter grid using product to get all combinations
        for params in product(param_grid['min_cluster_size'],
                            param_grid['min_samples'],
                            param_grid['cluster_selection_epsilon'],
                            param_grid['alpha'],
                            param_grid['metric']):

            min_cluster_size, min_samples, cluster_selection_epsilon, alpha, metric = params

            # Define the model with the current parameters
            hdb = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                cluster_selection_epsilon=cluster_selection_epsilon,
                alpha=alpha,
                metric=metric,
                prediction_data=True
            )

            # Fit the model
            labels = hdb.fit_predict(data_final_train)

            # Calculate the silhouette score
            if len(set(labels)) > 1:  # Silhouette score requires at least two clusters

                ##################################
                ##################################
                with mlflow.start_run(nested=True):
                ##################################
                ##################################

                    score = silhouette_score(data_final_train, labels)
                    labels_val, _ = hdbscan.approximate_predict(hdb, data_final_val)
                    try:    
                        score_val = silhouette_score(data_final_val, labels_val)


                    except :
                        score=score_val=0
                        print('182 -- ValueError: Number of labels is 1. Valid values are 2 to n_samples - 1 (inclusive)')
                    if score > best_score:
                        best_score = score
                        best_score_val = score_val
                        best_params = {
                            'min_cluster_size': min_cluster_size,
                            'min_samples': min_samples,
                            'cluster_selection_epsilon': cluster_selection_epsilon,
                            'alpha': alpha,
                            'metric': metric
                        }
                        best_labels = hdb.labels_

                    ######################################
                    ######################################
                    # Log parameters and metrics to MLflow
                    mlflow.log_params({
                        'min_cluster_size': min_cluster_size,
                        'min_samples': min_samples,
                        'cluster_selection_epsilon': cluster_selection_epsilon,
                        'alpha': alpha,
                        'metric': metric
                    })
                    mlflow.log_metric('silhouette_score', score)
                    mlflow.log_metric('silhouette_score_val', score_val)
                    ######################################
                    ######################################

        print("best params", best_params)
        print("best_score",best_score)
        print("best socre val",best_score_val)
        print("groups identified" ,set(best_labels))
        print(20*"{*}")
        print(20*"{*}")
        print(20*"{*}")
        print("EXPERIMENT NAME :",experiment_name )
        print(20*"{*}")
        print(20*"{*}")
        print(20*"{*}")

        # run un modele scikit learn avec les meilleur parametres

    from sklearn.cluster import HDBSCAN
    mlflow.set_experiment(experiment_name+"validation_modele_scikitlearn")
    mlflow.sklearn.autolog()
    with mlflow.start_run():
        hdb = HDBSCAN(**best_params)
        hdb.fit(data_final_train)
        mlflow.sklearn.log_model(hdb,'hdbscan_scikitlearn')




if __name__ == '__main__':
    run_optimisation()
