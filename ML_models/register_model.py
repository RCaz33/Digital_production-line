import os
import pickle
import click
import mlflow

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from mlflow.entities import ViewType

region = "France Central" # "West Europe"
subscription_id = "974386b8-dfe6-43cc-94af-17335974d64a"
resource_group = "mlops-promo"
workspace = "mlops-workspace-promo"
credentials = DefaultAzureCredential()

ml_client = MLClient(
    subscription_id=subscription_id,
    resource_group_name=resource_group,
    credential=credentials,)
ws = ml_client.workspaces.get(name=workspace)

mlflow.set_tracking_uri = ws.mlflow_tracking_uri
mlflow.set_experiment(experiment_name="k-means-groups")
mlflow.sklearn.autolog()

def load_pickle(filename):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


from sklearn.cluster import KMeans
from sklearn.metrics import rand_score

def train_and_log_model(data_path):
    X_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_test = load_pickle(os.path.join(data_path, "val.pkl"))
    with mlflow.start_run():
        for i in range(1,11):
            mlflow.log_param("groups_nbr", i)
            kmeans = KMeans(n_clusters=i, random_state=0, n_init="auto")
            w1 = kmeans.fit_transform(X_train) # metadata_ready.iloc[:120,1:]
            w2 = kmeans.fit_transform(X_test) # metadata_ready.iloc[40:,1:]
            rand_score = rand_score(w1[:-40], w2[:40])
            mlflow.log_metric("adj_rand_score", rand_score)

    



@click.command()
@click.option(
    "--data_path",
    default="./data",
    help="Location where the processed NYC taxi trip data was saved"
)
@click.option(
    "--top_n",
    default=5,
    type=int,
    help="Number of top models that need to be evaluated to decide which one to promote"
)

from azureml.core.experiment import Experiment

mlflow.search_experiments(view_type=ViewType.ALL)
mlflow.get_experiment_by_name("k-means-groups")

def run_register_model(data_path: str, top_n: int):

    client = MlflowClient()

    # Retrieve the top_n model runs and log the models
    experiment = Experiment(workspace=ws, name="k-means-groups")
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=top_n)#,
    #     order_by=["metrics.rmse ASC"]
    # )
    
    runs = experiment.get_runs()
    for run in runs:
        print(run)
        train_and_log_model(data_path=data_path, params=run.data.params)

    # # Select the model with the lowest test RMSE
    # experiment = client.get_experiment_by_name(EXPERIMENT_NAME)


    # ######################################

    # best_run = client.search_runs(
    #     experiment_ids=experiment.experiment_id,
    #     run_view_type=ViewType.ACTIVE_ONLY,
    #     max_results=top_n,
    #     order_by=["metrics.test_rmse ASC"]
    # )[0]                                        ######   top_n = 5, order by ASC so first index is best model

    # # Register the best model
    # model_run_id = best_run.info.run_id   ######  ==> print best_run to DEBUG, information in run is in .info
    # model_uri = f"runs:/{model_run_id}/model"
    # mlflow.register_model(model_uri,'rf-best-model')   


if __name__ == '__main__':
    run_register_model()
