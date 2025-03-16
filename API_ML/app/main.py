from fastapi import FastAPI,  Depends, HTTPException, status
import pandas as pd
from utils import *
app = FastAPI()
# import mlflow

##### Security token
from fastapi.security import APIKeyHeader
API_KEY_HEADER = APIKeyHeader(name="Supervized-API-Key")

# Store valid API keys (in a real application, store these securely)
import os
from dotenv import load_dotenv
load_dotenv()

valid_keys = os.getenv('API_SUPERVIZED_SECRET_KEY')

def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",)

@app.get("/info")
def info():
    return {"name":"API pour prédictions","version":"1.0.0"}

@app.post("/predict/{model_type}", dependencies=[Depends(verify_api_key)],response_model=Data_Out)
def predict(model_type:str,data:Data_In):

    

#    # connect to mlflow server
#     mlflow.set_tracking_uri('http://127.0.0.1:8080')
#     # load model and preprocessor
#     model_uri = "runs:/b46da47cde0649ecb2bc43292d977b48/logged_model"
#     model = mlflow.sklearn.load_model(model_uri)
#     local_path = mlflow.artifacts.download_artifacts(artifact_uri="runs:/dc7ae6946b33437b98c38447bdd9d140/2025-03-15_preprocessor.pkl")
#     import joblib
#     preprocessor = joblib.load(local_path)


    if model_type == "sgdreg":
        from sklearn.linear_model import SGDRegressor

    elif model_type == 'elasticnet':
        from sklearn.linear_model import ElasticNet

    import joblib
    preprocessor = joblib.load('data/2025-03-15_preprocessor.pkl')
    model = joblib.load('data/model.pkl')
    # prepare data
    X_clean = clean_data(pd.Series(data.dict()))
    X_transfo = preprocessor.transform(pd.DataFrame(X_clean).T)
    # preidct
    pred = model.predict(X_transfo)

    return {"pred":pred}


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app,host="0.0.0.0", port=1001)


### TEST API


# {
#   "Batch_OGD_name": "2301A",
#   "Batch_OGD_date": "2023-01-04",
#   "Batch_OGD_Technicien": "IT",
#   "Batch_OGD_KC8_batch": "K01",
#   "Batch_OGD_KC8_masse": 5.0,
#   "Batch_OGD_THF_batch": "to_fill",
#   "Batch_OGD_THF_Volume": 500.0,
#   "Batch_OGD_Temperature": 0,
#   "Batch_OGD_Agitation": 230.0,
#   "Batch_OGD_heure_debut": "2023-01-04 11:00:00",
#   "Batch_OGD_heure_fin": "2023-01-10 00:00:00",
#   "Batch_OGD_room_HR": 34.3,
#   "Batch_OGD_room_T": 20.0,
#   "Batch_OGD_Stock": 0,
#   "Batch_OGD_Analyses": "1"
# }