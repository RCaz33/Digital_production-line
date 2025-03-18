from fastapi import FastAPI,  Depends, HTTPException, status
import pandas as pd
# from app.main import app
from app.utils import *
app = FastAPI()
# import mlflow

##### Security token
from fastapi.security import APIKeyHeader
import json
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY_HEADER = APIKeyHeader(name="Supervized-API-Key")
valid_keys = os.getenv('API_SUPERVIZED_SECRET_KEYS')

def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if api_key not in json.loads(valid_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",)

@app.get("/info")
def info():
    return {"name":"API ML","version":"1.0.0"}

@app.post("/predict/{model_type}", dependencies=[Depends(verify_api_key)],response_model=Data_group_out)
def predict(model_type:str,data:Data_In):

    if model_type == "sgdreg":
        from sklearn.linear_model import SGDRegressor

    elif model_type == 'elasticnet':
        from sklearn.linear_model import ElasticNet

    import joblib

    preprocessor = joblib.load('app/data/ML_sup/2025-03-17_preprocessor.pkl')
    model = joblib.load('app/data/ML_sup/model.pkl')
    # prepare data
    X_clean = clean_data(pd.Series(data.model_dump()))
    X_transfo = preprocessor.transform(pd.DataFrame(X_clean).T)
    col_names = [a.replace('__','_') for a in preprocessor.get_feature_names_out()]
    # predict
    pred = model.predict(pd.DataFrame(X_transfo, columns=col_names))

    return {"pred":pred}

@app.get("/variable_importance", dependencies=[Depends(verify_api_key)])
def variable_importance():

    model = joblib.load('app/data/ML_sup/model.pkl')
    variable_importance = ({a:b for a,b in zip(model.feature_names_in_[model.coef_>0],model.coef_[model.coef_>0])})
    print(variable_importance)
    return variable_importance



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