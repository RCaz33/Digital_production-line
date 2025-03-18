from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import pandas as pd
import numpy as np
import joblib
from ML_un_2_preprocess_data import preprocess, preprocess_spectral
import hdbscan
from sklearn.manifold import TSNE
import pickle
import mlflow

################ SHEMAS #################
from typing import Dict, List, Any
from pydantic import BaseModel

class Data_prod(BaseModel):
    date : str
    metadata : Dict[str,Any]
    uv_data : Dict[str,Any]
    raman_data :  Dict[str,Any]

class Data_transformed(BaseModel):
    group : int
    label_tsne : List
    coord_tsne : List


app = FastAPI()
# Define the API key header
API_KEY_HEADER = APIKeyHeader(name="Unsupervized-API-Key")

# Store valid API keys (in a real application, store these securely)

SECRET_KEY_UNSUPERVIZED=["1234567", "12345678"]

def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if api_key not in SECRET_KEY_UNSUPERVIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )

@app.post("/transform_data", dependencies=[Depends(verify_api_key)], response_model=Data_transformed)
async def predict(request : Data_prod,where_from :str = 'local_db',date:str='2025-02-28'):


    # set source of model query
    if where_from == 'local':
        mlflow.set_tracking_uri('file:/data')   
    elif where_from == 'local_db':
        mlflow.set_tracking_uri('sqlite:///hdbscan.db')
    # elif where_to_log == 'new_db':
    #     mlflow.set_tracking_uri('http://127.0.0.1:8080')

    # elif where_from == 'remote':
    #     from azure.ai.ml import MLClient
    #     from azure.identity import DefaultAzureCredential

    #     subscription_id = "974386b8-dfe6-43cc-94af-17335974d64a"
    #     resource_group = "mlops-promo"
    #     workspace = "mlops-workspace-promo"

    #     ml_client = MLClient(credential=DefaultAzureCredential(),
    #                             subscription_id=subscription_id, 
    #                             resource_group_name=resource_group,
    #                             workspace_name=workspace)

    #     mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
    #     mlflow.set_tracking_uri(mlflow_tracking_uri)


    # get best model uri
    client = mlflow.MlflowClient()

    experiment = client.get_experiment_by_name(f"/{date}_training_dbscan_validation")

    best_run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=5,
        order_by=["metrics.silhouette_score_val ASC"]
    )[0]



    label = hdbscan.approximate_predict(model, data_out)[0]  # (label_array, strength_array)
    
    # label = model.predict(data_out)

    tsne = TSNE(n_components=2,random_state=0)
    with open(f'data/2025-02-26/transformed/train.pkl', 'rb') as file: 
        data = pickle.load(file).values
    
    coord_tsne = tsne.fit_transform(np.vstack([data, data_out]))
    print(type(coord_tsne))


    return {"group": label,"label_tsne":model.labels_.tolist(),"coord_tsne":coord_tsne.tolist()}

@app.get("/public-endpoint")
async def public_endpoint():
    return {"message": "This is a public endpoint"}


@app.get("/tsne_coordinates/{date}")
async def get_tsne_coordinates(date: str):
    # Load the saved t-SNE coordinates
    tsne_coord = joblib.load(f"data_API/{date}/weights_tsne.joblib")
    print(type(tsne_coord))
    print(tsne_coord.shape)
    return {"tsne_coordinates": tsne_coord.tolist()}
# To run the application, use the command: uvicorn your_script_name:app --reload




if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app,host="0.0.0.1", port=1000)










