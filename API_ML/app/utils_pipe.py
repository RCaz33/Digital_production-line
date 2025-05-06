#  initialisation des dependences
import requests
import logging
import pandas as pd
import click
import pickle
import random
from datetime import datetime
import os
import joblib
import mlflow
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder

# initialisation des connections externes
url = 'http://127.0.0.1:8000'
headers = {
'accept': 'application/json',
'Content-Type': 'application/json'}


def collect_metadata():
    """
    Cette fonction permet de collecter les données depuis une base de données externe
    et de les sauvegarder dans un fichier
    """
    # gestion des exeptions / erreurs
    try:
        response = requests.get(f'{url}/XY/', headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f" Cannot connect to database\nRequest failed: {e}")
    
    # traitement et sauvegarde pour entrainement ML 
    metadata = pd.DataFrame(response.json())
    return metadata

def collect_analyses():

    try:
        response = requests.get(f'{url}/analyses/', headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f" Cannot connect to database\nRequest failed: {e}")
    
    data_UV = pd.DataFrame([pd.Series(a['Analyses_data'],name=a['Analyse_name']) for a in response.json() if a['Analyse_subname'] == 'UV'])
    data_RAMAN = pd.DataFrame([pd.Series(a['Analyses_data'],name=a['Analyse_name']) for a in response.json() if a['Analyse_subname'] == 'RAMAN'])

    return data_UV, data_RAMAN


def preprocess_metadata(metadata: pd.DataFrame, sc: StandardScaler, ohe: OneHotEncoder, fit_dv : bool = False):
    
    time_columns = ['Batch_XY_date','Batch_XY_heure_debut','Batch_XY_heure_fin']
    timed = metadata[time_columns].copy()
    for col in timed.columns:
        timed.loc[:,col] = pd.to_datetime(timed[col])

    timed['year'] = pd.DatetimeIndex(timed['Batch_XY_date']).year.astype(str)
    timed['month'] = pd.DatetimeIndex(timed['Batch_XY_date']).month.astype(str)
    timed['time_exfo'] = (timed['Batch_XY_heure_fin'] - timed['Batch_XY_heure_debut']) / pd.Timedelta(hours=1)
    metadata_timed = pd.concat([metadata,timed],axis=1)

    numerical_columns = ['Batch_XY_XX_masse',
                        'Batch_XY_Temperature',
                        'Batch_XY_Agitation',
                        'Batch_XY_room_HR',
                        'Batch_XY_room_T',
                        'time_exfo']
    categorical_columns = ['Batch_XY_Technicien',
                            'Batch_XY_XX_batch',
                            'Batch_XY_YY_batch',
                            'year',
                            'month']

    if fit_dv:
        scaled = sc.fit_transform(metadata_timed[numerical_columns])
        scaled = pd.DataFrame(scaled, columns=numerical_columns, index=metadata.Batch_XY_name)
        onehotencoded = ohe.fit_transform(metadata_timed[categorical_columns])
        onehotencoded = pd.DataFrame(onehotencoded, columns = [a for b in ohe.categories_ for a in b], index=metadata.Batch_XY_name)
    else:
        scaled = sc.transform(metadata_timed[numerical_columns])
        scaled = pd.DataFrame(scaled, columns=numerical_columns, index=metadata.Batch_XY_name)
        onehotencoded = ohe.transform(metadata_timed[categorical_columns])
        onehotencoded = pd.DataFrame(onehotencoded, columns = [a for b in ohe.categories_ for a in b], index=metadata.Batch_XY_name)

    metadata_ready = pd.concat([scaled,onehotencoded],axis=1)


    return metadata_ready, sc, ohe

def preprocess_spectral(idx_train, idx_val, data_raman, data_uv, mode='pca'):
    """ this function takes in spectral data c.a; UV and Raman
    and preprocesses it using PCA, TSNE or FastICA
    it returns the transformed data concatenated and the fitted transformer"""

    data_raman_train = data_raman[data_raman.index.isin(idx_train)].sort_index()
    data_raman_val = data_raman[data_raman.index.isin(idx_val)].sort_index()    
    
    data_uv_train = data_uv[data_uv.index.isin(idx_train)].sort_index()
    data_uv_val = data_uv[data_uv.index.isin(idx_val)].sort_index()

    if mode == 'pca':
        from sklearn.decomposition import PCA
        reduce_r = PCA(n_components=10)
        if any(data_raman_train):
            data_raman_train_weights = reduce_r.fit_transform(data_raman_train)
            data_raman_val_weights = reduce_r.transform(data_raman_val)
        reduce_uv = PCA(n_components=10)
        if any(data_uv_train):
            data_uv_train_weights = reduce_uv.fit_transform(data_uv_train)
            data_uv_val_weights = reduce_uv.transform(data_uv_val)

    elif mode == 'tsne':
        from sklearn.manifold import TSNE
        reduce_r = TSNE(n_components=10)
        if any(data_raman_train):
            data_raman_train_weights = reduce_r.fit_transform(data_raman_train)
            data_raman_val_weights = reduce_r.transform(data_raman_val)
        reduce_uv = TSNE(n_components=10)
        if any(data_uv_train):
            data_uv_train_weights = reduce_uv.fit_transform(data_uv_train)
            data_uv_val_weights = reduce_uv.transform(data_uv_val)

    elif mode == 'fastica':
        from sklearn.decomposition import FastICA
        reduce_r = FastICA(n_components=10)
        if any(data_raman_train):
            data_raman_train_weights = reduce_r.fit_transform(data_raman_train)
            data_raman_val_weights = reduce_r.transform(data_raman_val)
        reduce_uv = FastICA(n_components=10)
        if any(data_uv_train):
            data_uv_train_weights = reduce_uv.fit_transform(data_uv_train)
            data_uv_val_weights = reduce_uv.transform(data_uv_val)

    if any(data_raman_train):
        out_train = pd.DataFrame(np.concatenate([data_uv_train_weights,
                                                data_raman_train_weights],axis=1),
                                                index=data_raman_train.index)
        out_val = pd.DataFrame(np.concatenate([data_uv_val_weights,
                                                data_raman_val_weights],axis=1),
                                                index=data_raman_val.index)  
    else:
        out_train = pd.DataFrame(data_uv_train_weights, index=data_uv_train.index)
        out_val = pd.DataFrame(data_uv_val_weights, index=data_uv_val.index)
   
    return out_train, out_val, reduce_r, reduce_uv




def run_optimisation(where_to_log:str, train_val_split:int, mode:str):

    if where_to_log == 'db_in_docker':
        print("SPECIFIC_DB")
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASS')
        db = os.getenv('DB_NAME')
        container_name = "mysql-db"
        mlflow.set_tracking_uri(f'mysql+pymysql://{user}:{password}@{container_name}/{db}')

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


    elif where_to_log == 'test':
        mlflow.set_tracking_uri("file:./tracking_mlflow")

    elif where_to_log == 'local':
        mlflow.set_tracking_uri("sqlite:///data/ML_Flow_db.db")
    
    #load data
    meta = collect_metadata()
    uv, raman = collect_analyses()

    # prepare data
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
    meta_train, sc_fit, ohe_fit = preprocess_metadata(meta.loc[meta['Batch_XY_name'].isin(idx_train)].sort_values('Batch_XY_name'),
                                        sc,ohe,fit_dv=True)
    meta_val, _, _ = preprocess_metadata(meta.loc[meta['Batch_XY_name'].isin(idx_val)].sort_values('Batch_XY_name'),
                                        sc_fit,ohe_fit,fit_dv=False)
    out_train, out_val, reduce_r, reduce_uv = preprocess_spectral(idx_train,idx_val, raman, uv, mode=mode)
    # combine data

    data_final_train = pd.merge(meta_train, out_train, left_index=True, right_index=True, how='inner')
    data_final_train.columns = data_final_train.columns.astype(str)
    data_final_val = pd.merge(meta_val, out_val, left_index=True, right_index=True)
    data_final_val.columns = data_final_val.columns.astype(str)


    # Log data
    # set experiment
    date = datetime.now().strftime('%Y-%m-%d')
    print(date)
    experiment_name = f"hdbscan_{date}"
    mlflow.set_experiment(experiment_name)
    # mlflow.autolog()

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
    from itertools import product
    import hdbscan
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
                from sklearn.metrics import silhouette_score, davies_bouldin_score

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

        all_data = pd.concat([data_final_train,data_final_val])
        print(all_data.shape,data_final_train.shape,data_final_val.shape)
        hdb.fit(all_data)
        mlflow.sklearn.log_model(hdb,'hdbscan_scikitlearn')

    return best_labels


