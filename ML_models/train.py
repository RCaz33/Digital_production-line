import os
import pickle
import click

from sklearn.cluster import KMeans
from sklearn.metrics import rand_score

##############
import mlflow

##############


#####################
region = "France Central" # "West Europe"
subscription_id = "974386b8-dfe6-43cc-94af-17335974d64a"
resource_group = "mlops-promo"
workspace = "mlops-workspace-promo"
# azureml_mlflow_uri = f"azureml://{region}.api.azureml.ms/mlflow/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}"
# mlflow.set_tracking_uri(azureml_mlflow_uri)
credentials = DefaultAzureCredential()
ml_client = MLClient(
    subscription_id=subscription_id,
    resource_group_name=resource_group,
    credential=credentials,)
ws = ml_client.workspaces.get(name=workspace)
####################

# mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_tracking_uri = ws.mlflow_tracking_uri
mlflow.set_experiment(experiment_name="k-means-groups")

def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./data",
    help="Location where the processed data was saved"
)
def run_train(data_path: str):


    ############################
    mlflow.sklearn.autolog()
    #####################


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


if __name__ == '__main__':
    run_train()
