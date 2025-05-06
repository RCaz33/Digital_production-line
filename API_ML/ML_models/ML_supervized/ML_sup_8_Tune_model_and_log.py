# import des librairies
import os
import click
import requests
import mlflow
import numpy as np
import pandas as pd
import joblib
from datetime import datetime

from sklearn.linear_model import ElasticNetCV, ElasticNet
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import cross_validate
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

######### ENVIRON VARIABLE
# export MLFLOW_ARTIFACT_URI="file:/path" 
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient

# test if tracking server
def test_tracking_server_connection_ok(tracking_uri):
    print("IS TESTING TRACKING URI ...")
    try: # use timeout to avoid waiting for ever
        response = requests.get(f"{tracking_uri}/health", timeout=5)
        if response.status_code == 200:
            return "connection à MLFlow ok"
    except:
        return "connection au serveur mlmflow impossible"

# load data
def load_data(raw_data_path):
    """ this function tries to load data if it exist"""
    try:
        X = X = pd.read_csv(f"{raw_data_path}/new_X.csv",index_col=0)
        y = pd.read_csv(f"{raw_data_path}/y.csv",index_col=0)
        y = y['QC_Conc_XY'].astype(float)
        return X, y
    except:
        return "les données n'existent pas, essayez de les générer / nettoyer en premier ou changez de dossier"

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
        preprocessor.fit(X.iloc[:2,:])
        return preprocessor
    except:
        return ("set_preprocessor is not working, check columns names")

# prepare data for ML
def get_best_params_elasticnet(X,y,tracking_uri,date):
    """this function instanciate and test a sklearn preprocessor"""

    # cherche les meilleurs hyperparametres
    cv_model = ElasticNetCV(l1_ratio=[.1, .3, .5, .8, .9, .95, .995, 1], eps=0.001, n_alphas=20, fit_intercept=True, 
                            precompute=True, max_iter=10000, tol=0.0001, cv=ShuffleSplit(n_splits=10,test_size=0.2), 
                            copy_X=True, verbose=0, n_jobs=-1, positive=False, random_state=42, selection='cyclic')
    pipe = Pipeline([('preprocessor',set_preprocessor(X)),
                     ('cv_model',cv_model)])
    pipe.fit(X,y)

    # Extract the MSE path, the alphas and l1_ratiospython
    mse_path = pipe.named_steps["cv_model"].mse_path_
    alphas = [float(a) for a in cv_model.alphas_[0]] #cv_model.alphas_
    l1_ratios = cv_model.l1_ratio
    # Iterate over each combination of alpha and l1_ratio
    print("START LOGGING ELASTICNET CV SEARCH")          
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(f"{date}_ElasticNetCV_hyperparams_search")
    for j, l1_ratio in enumerate(l1_ratios):
        for i, alpha in enumerate(alphas):
            with mlflow.start_run(nested=True, run_name='CV_elastincnet'):
                # Calculate the mean/std MSE for this combination and log to mlflow
                mean_mse, std_mse = np.mean(mse_path[j, i, :]), np.std(mse_path[j, i, :])
                print(l1_ratio)
                mlflow.log_params({'alpha':alpha,'l1_ratio':l1_ratio})
                mlflow.log_metrics({'mean_squared_error':mean_mse,
                                    'mse_std':std_mse})
    mlflow.end_run()
    print("END LOGGING ELASTICNET CV SEARCH")          
    print("best l1 ratio",cv_model.l1_ratio_)
    print("best alpha",cv_model.alpha_)
    return cv_model.l1_ratio_, cv_model.alpha_

def get_best_params_sgdregr(X, y, tracking_uri, date):

    # Définir l'espace des hyperparamètres
    param_dist = {
        'loss': ['squared_error', 'huber', 'epsilon_insensitive'],
        'penalty': ['l2', 'l1', 'elasticnet'],
        'alpha': [0.0001, 0.001, 0.01, 0.1],
        'learning_rate': ['constant', 'optimal', 'invscaling', 'adaptive'],
        'eta0': [0.01, 0.1, 0.2],
        'max_iter': [500, 1000, 1500]}

    # Effectuer la recherche aléatoire
    sgd_regressor = SGDRegressor(random_state=42)
    random_search = RandomizedSearchCV(sgd_regressor, param_distributions=param_dist, n_iter=100, 
                                       cv=5, scoring='root_mean_squared_error' , random_state=42, # 'neg_mean_squared_error'
                                       return_train_score=True)
    pipe = Pipeline([('preprocessor',set_preprocessor(X)),
                     ('random_search',random_search)])
    pipe.fit(X,y)


    results = pd.DataFrame(pipe.named_steps["random_search"].cv_results_).sort_values(by='rank_test_score')
    print("START LOGGING SGD RANDOM SEARCH")
    # log sur ML-Flow
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(f"{date}_ElasticNetCV_hyperparams_search")
    for i in range(results.shape[0]):
        with mlflow.start_run(nested=True, run_name='CV_sgdregr'):
            mlflow.log_params(results.loc[i,'params'])
            mlflow.log_metrics({'mean_fit_time':results.loc[i,'mean_fit_time'],
                                'mean_test_score':results.loc[i,'mean_test_score'],
                                'std_test_score':results.loc[i,'std_test_score'],
                                'mean_train_score':results.loc[i,'mean_train_score'],
                                'std_train_score':results.loc[i,'std_train_score']})
    mlflow.end_run()
    print("END LOGGING SGD RANDOM SEARCH")
    # Meilleurs hyperparamètres
    return pipe.named_steps["random_search"].best_params_


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
@click.option(
    "--algo_type", default="elasticnet", prompt='which model?',
    help="modèle ML à utiliser pour la recherche d'hyperparametres"
)


def log_best_elastic_net_model(tracking_uri : str, raw_data_path : str, algo_type : str):

    """ search best hyperparameters for elasticnet
    uses mlflow to register experiment by date,
    can save artifact locally or on blob storage"""

    # test connection to tracking server
    _ = test_tracking_server_connection_ok(tracking_uri)

    # prepare data and preprocessing
    X, y = load_data(raw_data_path)
   
    # get best params for a given date
    date = datetime.now().strftime('%Y-%m-%d')

    # Cross-validation with best params
    if algo_type == 'elasticnet':
        best_l1_ratio, best_alpha = get_best_params_elasticnet(X,y,tracking_uri,date)
        # cross validated score for elastic net 
        model = ElasticNet(alpha=best_alpha, l1_ratio=best_l1_ratio, fit_intercept=True, 
                    precompute=True, max_iter=10000, tol=0.0001,
                    copy_X=True, positive=True, random_state=42, selection='cyclic')
        pipe = Pipeline([('preprocessor',set_preprocessor(X)),
                    ('model',model)])
    
        results = cross_validate(pipe,X,y,cv=ShuffleSplit(n_splits=15,test_size=0.2),
                            return_train_score=True,
                            scoring="neg_root_mean_squared_error")

    elif algo_type == 'sgdregr':
        best_params = get_best_params_sgdregr(X,y,tracking_uri,date)
        model = SGDRegressor(**best_params)
        pipe = Pipeline([('preprocessor',set_preprocessor(X)),
                    ('model',model)])
        results = cross_validate(pipe,X,y,cv=ShuffleSplit(n_splits=15,test_size=0.2),
                            return_train_score=True,
                            scoring="neg_root_mean_squared_error")
        

    # configure mflflow
    print("START LOGGING FINAL MODEL")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(f"/{date}_Tune_model_and_log")
    # mlflow.autolog()

    # log results of cross-validation
    with mlflow.start_run(run_name=f"CrossValidate_{algo_type}"):
        # log mean of variables for n CVs
        for i in range (results['fit_time'].shape[0]):
            mlflow.log_param("model",algo_type)
            mlflow.log_metrics({k:-v[i] for k,v in results.items()})
        print('ACTIVE RUN_ID - for logging cv resulsts without model',mlflow.active_run().info.run_id)   


    # results = pd.DataFrame(cv)

    
    # log model and artifact trained on the entire dataset
    with mlflow.start_run(run_name=f"{date}_{algo_type}_best_model_run") as run:
        run_id = run.info.run_id 
        print('ACTIVE RUN_ID - after start run',mlflow.active_run().info.run_id)   

        # fit the preprocessor and model
        preprocessor = set_preprocessor(X)
        print(X.shape)
        X = preprocessor.fit_transform(X)
        print(X.shape)
        col_names = [a.replace('__','_') for a in preprocessor.get_feature_names_out()]
        X = pd.DataFrame(X,columns=col_names)
        _ = model.fit(X,y)
        preds = model.predict(X)



        # log predictions

        # first log preprocessor 
        preprocessor_name = f"{date}_preprocessor.pkl"
        joblib.dump(preprocessor, preprocessor_name)
        mlflow.log_artifact(preprocessor_name)
        os.remove(preprocessor_name)

        # log variable name and coef if coef > 0 
        params_to_log={a.replace('__','_'):b for a,b in zip(preprocessor.get_feature_names_out()[model.coef_>0],model.coef_[model.coef_>0])}
        print(params_to_log)
        mlflow.log_param("model",algo_type)
        try:
            mlflow.log_metrics(params_to_log)
        except Exception as e:
            print(e)
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


if __name__ == '__main__':
    log_best_elastic_net_model()
