# import des librairies
import click
import requests
import mlflow
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.linear_model import ElasticNetCV, ElasticNet
from sklearn.model_selection import cross_validate
from sklearn.model_selection import ShuffleSplit
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

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
        X = X = pd.read_csv(f"{raw_data_path}/X.csv",index_col=0)
        y = pd.read_csv(f"{raw_data_path}/y.csv",index_col=0)
        y = y['QC_Conc_OGD'].astype(float)
        return X, y
    except:
        return "les données n'existent pas, essayez de les générer / nettoyer en premier ou changez de dossier"

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

# prepare data for ML
def get_best_params(X,y,tracking_uri,date):
    """this function instanciate and test a sklearn preprocessor"""

    # cherche les meilleurs hyperparametres
    cv_model = ElasticNetCV(l1_ratio=[.1, .5, .9, .95, .995, 1], eps=0.001, n_alphas=50, fit_intercept=True, 
                            precompute=True, max_iter=10000, tol=0.0001, cv=ShuffleSplit(n_splits=10,test_size=0.2), 
                            copy_X=True, verbose=0, n_jobs=-1, positive=False, random_state=42, selection='cyclic')
    cv_model.fit(X,y)

    # Extract the MSE path, the alphas and l1_ratios
    mse_path = cv_model.mse_path_
    alphas = [float(a) for a in cv_model.alphas_[0]] #cv_model.alphas_
    l1_ratios = cv_model.l1_ratio
    # Iterate over each combination of alpha and l1_ratio
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(f"{date}_ElasticNetCV_hyperparams_search")
    for j, l1_ratio in enumerate(l1_ratios):
        for i, alpha in enumerate(alphas):
            with mlflow.start_run(nested=True):
            # Calculate the mean/std MSE for this combination and log to mlflow
                mean_mse, std_mse = np.mean(mse_path[j, i, :]), np.std(mse_path[j, i, :])
                print(l1_ratio)
                mlflow.log_params({'alpha':alpha,'l1_ratio':l1_ratio})
                mlflow.log_metrics({'mean_squared_error':mean_mse,
                                    'mse_std':std_mse})
                                
    # print("Mean square error for the test set on each fold",cv_model.mse_path_)
    print("best l1 ratio",cv_model.l1_ratio_)
    print("best alpha",cv_model.alpha_)
    return cv_model.l1_ratio_, cv_model.alpha_



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
    "--log_method", default="after_run_completed", prompt='where to log model?',
    help="Dossier ou les artifcat (model.pkl) sont stockées"
)


def log_best_elastic_net_model(tracking_uri : str, raw_data_path : str, log_method : str):

    """ search best hyperparameters for elasticnet
    uses mlflow to register experiment by date,
    can save artifact locally or on blob storage"""

    # test connection to tracking server
    _ = test_tracking_server_connection_ok(tracking_uri)

    # prepare data and preprocessing
    X, y = load_data(raw_data_path)
    preprocessor = set_preprocessor(X)
    X = preprocessor.transform(X)

    # get best params
    date = datetime.now().strftime('%Y-%m-%d')
    best_l1_ratio, best_alpha = get_best_params(X,y,tracking_uri,date)

    # cross validated score for best model   
    en = ElasticNet(alpha=best_alpha, l1_ratio=best_l1_ratio, fit_intercept=True, 
                precompute=True, max_iter=10000, tol=0.0001,
                copy_X=True, positive=True, random_state=42, selection='cyclic')

    results = cross_validate(en,X,y,cv=ShuffleSplit(n_splits=15,test_size=0.2),
                        return_train_score=True,
                        scoring="neg_root_mean_squared_error")

    # results = pd.DataFrame(cv)

    # configure mflflow
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(f"/{date}_Cross_validate_ElasticNet_v1_2")
    # mlflow.autolog()

    with mlflow.start_run(run_name=f"{date}_best_model_run") as run:
        run_id = run.info.run_id    
       # log mean of variables for n CVs
        mlflow.log_metrics({k:np.mean(v) for k,v in results.items()})
        _ = en.fit(X,y)
         # log variable name and coef if coef > 0 
        mlflow.log_params({a:b for a,b in zip(preprocessor.get_feature_names_out()[en.coef_>0],en.coef_[en.coef_>0])})

        
        if log_method == "log-flavor":
            mlflow.sklearn.log_model(sk_model=en,
                                     signature=infer_signature(X[:10,:],en.predict(X[:10,:])),
                                     registered_model_name=f"best_model_on_{date}", # this allow to log and to register at the same time
                                     artifact_path ="data/model") # if azure, make sure to set atifcact path as model:/experiemtname/model
    
        
    if log_method == "after_run_completed": # save model artifcat in folder --default-artifact-root
        result = mlflow.register_model(f"runs:/{run_id}/", "best_model_on_{date2}")
        log = mlflow.sklearn.log_model(en,"best_model_on_{date2}",
                                       signature=infer_signature(X[:10,:],en.predict(X[:10,:])))
        
    # mlflow.log_artifact('dataset_transformed')  # SAVE DATASET IN MLFLOW ?

    print(f"MODEL_URI : runs:/{run_id}/data/model")
    # elif log_method == "create registered model":
    #     client = MlflowClient()
    #     result = client.create_model_version(name="best_model_on_{date}",
    #                                          source="artifact/")


if __name__ == '__main__':
    log_best_elastic_net_model()
