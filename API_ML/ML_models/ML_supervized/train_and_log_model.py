# import general librairies
import os
import pickle
import click
import mlflow

# import azure / mlflow librairies
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from mlflow.entities import ViewType
from azureml.core.experiment import Experiment
from azureml.core.model import Model

# impor sklearn librairies
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import GridSearchCV

from dotenv import load_dotenv
load_dotenv()

def configure_azure(region : str = os.getenv('SIMPLON_AZURE_REGION'), # "West Europe"
                subscription_id : str = os.getenv('SIMPLON_AZURE_SUBSCRIPTION_ID'),
                resource_group : str = os.getenv('SIMPLON_AZURE_RESSOURCE_GROUP'),
                workspace : str = os.getenv('SIMPLON_AZURE_WORKSPACE')):
    
    credentials = DefaultAzureCredential()
    ml_client = MLClient(
        region=region,
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        credential=credentials,)
    ws = ml_client.workspaces.get(name=workspace)
    return ws

def load_pickle(filename):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)



@click.command()
@click.option(
    "--data_path",
    default="./data",
    help="Location where the processed data was saved"
)
@click.option(
    "--top_n",
    default=5,
    type=int,
    help="Number of top models that need to be evaluated to decide which one to promote"
)


def train_and_log_model(data_path :str, experiment_name : str = "try_linear_models"):

    ws = configure_azure()

    X = load_pickle(os.path.join(data_path, "X.pkl"))
    y = load_pickle(os.path.join(data_path, "y.pkl"))

    models_and_params = {
        LinearRegression: {},
        ElasticNet: {'alpha': [0.1, 1.0, 10.0], 'l1_ratio': [0.1, 0.5, 0.9]},
        RandomForestRegressor: {'n_estimators': [100, 200], 'max_depth': [None, 10, 20]}
    }

    mlflow.set_tracking_uri(ws.mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name=experiment_name)
    mlflow.sklearn.autolog()

    with mlflow.start_run():
        for model_class, param_grid in models_and_params.items():

            mlflow.log_param("model", model_class.__name__)
            model = model_class()

            # Hyperparameter search with cross-validation
            grid_search = GridSearchCV(model, param_grid, cv=5, scoring='neg_mean_squared_error')
            grid_search.fit(X, y)

            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metric(grid_search.best_score_)
            mlflow.sklearn.log_model("best_{best_model}_model", grid_search.best_estimator_)

            # Save the best model to Azure ML
            model_name = f"best_{model_class.__name__}_model"
            Model.register(workspace=ws, model_path=model_name, model=grid_search.best_estimator_)


if __name__ == '__main__':
    train_and_log_model()
