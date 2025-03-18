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

from itertools import product
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

from dotenv import load_dotenv

load_dotenv()
user = os.getenv('LOCAL_DB_USER')
password = os.getenv('LOCAL_DB_PASS')
db = os.getenv('LOCAL_DB_MLFLOW')

DBSCAN_EXPERIMENT_NAME='/'
DBSCAN_PARAMS = ['min_cluster_size', 'min_samples', 'cluster_selection_epsilon', 'alpha', 'metric']

def dump_pickle(obj, filename: str):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)

def load_pickle(filename:str):
    with open(filename, 'rb') as file:
        return pickle.load(file)
    


def retrain_model(data_path, params):


    train = load_pickle(os.path.join(data_path, "ML_ready/train.pkl"))
    val = load_pickle(os.path.join(data_path, "ML_ready/val.pkl"))



    with mlflow.start_run():
        new_params={}
        for param in DBSCAN_PARAMS:
            if not param == 'metric':
                try:
                    new_params[param] = int(params[param])
                except:
                    new_params[param] = float(params[param])
            else:
                new_params[param] = params[param]
            new_params['prediction_data'] = True

        hdb = hdbscan.HDBSCAN(**new_params)
        labels = hdb.fit_predict(train)
        labels_val, _ = hdbscan.approximate_predict(hdb,val)

        print(set(labels))

        try:
            train_score = silhouette_score(train, labels)
            val_score = silhouette_score(val, labels_val)
            mlflow.log_metric('silhouette_score', train_score)
            mlflow.log_metric('silhouette_score_val', val_score)

        except ValueError as e:
            print("HAAAAAAAA",e)


@click.command()
@click.option(
    "--data_path",default='data/2025-02-26', prompt='Location of the raw data',
    help="Location where the raw data was saved"
)
# @click.option(
#     "--dest_path",
#     help="Location where the resulting files will be saved"
# )
# @click.option(
#     "--mode",  default='pca', prompt='Mode of spectral reduction', help="Mode of spectral reduction"
# )
@click.option(
    "--experiment_name",  default='/hdbscan_2025-02-28', prompt='what experiment', help="Mode of spectral reduction"
)
@click.option(
    "--where_to_log",  default='specific_db', prompt='Where to connect to MLFLow logs', help="Mode of spectral reduction"
)



def run_register_model(data_path : str , experiment_name : str, where_to_log : str = 'local'):

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
        mlflow.set_tracking_uri('sqlite:///hdbscan.db')

    elif where_to_log == 'specific_db':
        user = os.getenv('LOCAL_DB_USER')
        password = os.getenv('LOCAL_DB_PASS')
        db = os.getenv('LOCAL_DB_MLFLOW')

        mlflow.set_tracking_uri(f'mysql+pymysql://{user}:{password}@localhost/{db}')

    elif where_to_log == 'remote':
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



    # Retrieve the top_n model runs and log the models
    client = MlflowClient()
    experiment = client.get_experiment_by_name(experiment_name)
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=5,
        order_by=["metrics.silhouette_score ASC"]
    )
    for run in runs:
        retrain_model(data_path=data_path, params=run.data.params)

    # Select the model with the lowest test RMSE
    # experiment = client.get_experiment_by_name(EXPERIMENT_NAME)


    ######################################

    best_run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=5,
        filter_string="metrics.silhouette_score > 0",
        order_by=["metrics.silhouette_score_val ASC"]
    )[0]                                        ######   top_n = 5, order by ASC so first index is best model

    try : 
        # Register the best model
        model_run_id = best_run.info.run_id   ######  ==> print best_run to DEBUG, information in run is in .info
        model_uri = f"runs:/{model_run_id}/model"
        mlflow.register_model(model_uri,'rf-best-model')   

    except:
        print("OOOOOOh, only bad models")


if __name__ == '__main__':
    run_register_model()
